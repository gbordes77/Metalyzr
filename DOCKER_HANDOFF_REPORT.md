# Rapport de Handoff : Point de Blocage Docker - Service Backend

**À l'attention de l'expert Docker,**

Ce document résume l'état du projet, le problème de build persistant sur le service `backend`, et toutes les tentatives de résolution effectuées. L'objectif est de vous fournir un contexte maximal pour un diagnostic rapide.

## 1. Objectif

L'objectif est de faire fonctionner une application FastAPI conteneurisée (`backend`) via `docker-compose`. L'environnement complet inclut également un frontend React (`frontend`), une base de données (`postgres`) et un cache (`redis`).

**Les services `frontend`, `postgres`, et `redis` se construisent et se lancent correctement.** Le blocage est uniquement sur le service `backend`.

## 2. Le Problème Final

Après de multiples itérations, l'erreur finale et persistante lors du `docker-compose up` est :

```bash
OCI runtime create failed: ... exec: "uvicorn": executable file not found in $PATH: unknown
```

Cette erreur survient au moment de lancer la `CMD` du conteneur `backend`.

## 3. État Actuel du `backend/Dockerfile`

Voici le contenu du `backend/Dockerfile` dans son état le plus récent et logiquement le plus correct. C'est sur cette version que le problème persiste.

```dockerfile
# ---- 1. Stage Builder : Installation des dépendances ----
FROM python:3.11-slim as builder

# Pré-requis système pour certaines librairies Python
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Définir le répertoire de travail
WORKDIR /app

# Installer Poetry
RUN pip install poetry

# Configurer Poetry pour créer le .venv dans le projet
RUN poetry config virtualenvs.in-project true

# Copier uniquement les fichiers de dépendances pour profiter du cache Docker
COPY poetry.lock pyproject.toml ./

# Installer les dépendances du projet
RUN poetry install --no-interaction --no-ansi --no-root


# ---- 2. Stage Final : Création de l'image de production ----
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Créer un utilisateur et un groupe non-root pour la sécurité
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copier l'environnement virtuel depuis le builder.
COPY --chown=appuser:appgroup /app/.venv ./.venv

# Copier le code de l'application. On copie TOUT le contenu du contexte (le dossier backend)
COPY --chown=appuser:appgroup . .

# Changer d'utilisateur pour ne pas exécuter en root
USER appuser

# Commande pour démarrer l'application.
# On utilise le chemin ABSOLU vers l'exécutable et on pointe vers "main:app"
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Logique de ce Dockerfile :**
1.  Un stage `builder` installe les dépendances via `Poetry` dans un environnement virtuel local au projet (`/app/.venv`). Cette étape se termine avec succès.
2.  Un stage `final` part d'une image propre.
3.  Il copie l'environnement virtuel (`.venv`) et le code source depuis le `builder`.
4.  Il crée un utilisateur `appuser` et lui donne la propriété de tous les fichiers.
5.  Il tente d'exécuter `uvicorn` en utilisant le chemin absolu vers l'exécutable situé dans le `.venv` copié.

## 4. Itérations et Tentatives de Résolution (Toutes Infructueuses)

Voici un résumé des approches qui ont été tentées et ont mené à la même erreur finale :

- **Utilisation de `ENV PATH` :** L'ajout de `ENV PATH="/app/.venv/bin:$PATH"` dans l'image finale n'a pas permis de résoudre l'exécutable. La `CMD ["uvicorn", ...]` échouait toujours.
- **Utilisation de `poetry run` :** Tenter `CMD ["poetry", "run", ...]` a échoué car `poetry` lui-même n'est pas installé dans l'image finale (uniquement dans le `builder`).
- **Simplification des permissions :** Des variantes avec des `chown` séparés ou combinés à la création de l'utilisateur ont été testées.
- **Ordre des `COPY` et `chown` :** Différents ordres ont été testés sans succès.
- **Chemins de copie :** Les chemins de `COPY` ont été la source de plusieurs erreurs intermédiaires (`file not found` au build), mais ces erreurs ont été corrigées pour arriver à la version actuelle du Dockerfile qui passe bien l'étape du build.

## 5. Le Symptôme le plus Déroutant

Même en utilisant un chemin absolu dans la `CMD` (`["/app/.venv/bin/uvicorn", ...]`), l'erreur reste `executable file not found`.

**Hypothèse :** Le problème pourrait être lié au *shebang* du script `uvicorn`. Le script commence par `#!/app/.venv/bin/python`. Si l'interpréteur Python spécifié dans ce shebang n'est pas trouvé ou accessible au moment de l'exécution, le système d'exploitation peut remonter une erreur "file not found" pour le script lui-même.

## 6. Pistes d'Investigation pour l'Expert

1.  **Inspecter l'image finale :**
    *   Lancer un conteneur interactif à partir de l'image buildée (`docker run -it --entrypoint /bin/sh <image_id>`).
    *   Vérifier si le dossier `/app/.venv/bin` et son contenu existent bien.
    *   Vérifier les permissions (`ls -la /app` et `ls -la /app/.venv/bin`).
    *   Tenter d'exécuter `/app/.venv/bin/uvicorn --version` manuellement.
    *   Vérifier le contenu du shebang avec `head -n 1 /app/.venv/bin/uvicorn`.
    *   Vérifier si l'interpréteur du shebang (`/app/.venv/bin/python`) est exécutable.
2.  **Simplifier pour isoler :**
    *   Essayer de lancer une commande plus simple dans la `CMD`, comme `["ls", "-la", "/app"]`, pour confirmer que l'utilisateur et le `WORKDIR` sont corrects.
    *   Remplacer la `CMD` par un `ENTRYPOINT` avec le chemin absolu.

Je vous remercie de votre temps et de votre expertise. L'ensemble du code est disponible sur le dépôt pour analyse. 