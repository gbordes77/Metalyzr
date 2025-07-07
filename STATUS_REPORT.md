# Metalyzr - État des Lieux et Point de Blocage

Ce document décrit l'état actuel du projet au moment de sa rédaction et détaille le problème technique qui empêche le démarrage complet de l'environnement de développement.

## Statut Global

- ✅ **Services de base :** Les conteneurs `postgres` et `redis` démarrent et sont stables.
- ✅ **Frontend :** Le conteneur `frontend` se construit avec succès. L'application React est buildée et servie par Nginx.
- 🚨 **Backend :** Le conteneur `backend` se construit avec succès, mais **échoue au démarrage**.

## Point de Blocage : Démarrage du Service Backend

Le problème se situe dans l'exécution de la commande finale du `backend/Dockerfile`.

### L'Erreur

Après une série de tentatives et de corrections, l'erreur persistante est :
```bash
OCI runtime create failed: ... exec: "uvicorn": executable file not found in $PATH: unknown
```

Cette erreur signifie que le système d'exploitation à l'intérieur du conteneur final ne trouve pas l'exécutable `uvicorn` pour lancer le serveur FastAPI, même après que celui-ci a été installé par `Poetry`.

### Analyse du Problème

Le `backend/Dockerfile` utilise une approche multi-stage pour créer une image légère.

1.  **Stage `builder` :** Installe `Poetry` et les dépendances du projet (y compris `uvicorn`) dans un environnement virtuel situé à `/app/.venv`. Cette étape se déroule sans erreur.
2.  **Stage final :**
    - Part d'une image Python propre.
    - Copie l'environnement virtuel `.venv` depuis le stage `builder`.
    - Copie le code de l'application.
    - Ajoute le chemin des exécutables du venv au `PATH` global (`ENV PATH="/app/.venv/bin:$PATH"`).
    - Crée un utilisateur non-root `appuser`.
    - Change le propriétaire des fichiers pour `appuser`.
    - Tente de lancer `CMD ["uvicorn", ...]`.

Le problème se situe dans la résolution du `PATH` pour l'utilisateur `appuser` au moment de l'exécution de la `CMD`. Malgré toutes les tentatives, l'exécutable `uvicorn`, qui se trouve bien dans `/app/.venv/bin/`, n'est pas trouvé.

### Tentatives de Résolution (Infructueuses)

1.  **Appel direct via `poetry run` :** Échoue car `poetry` lui-même n'existe pas dans l'image finale.
2.  **Chemin absolu vers l'exécutable :** La commande `CMD ["/app/.venv/bin/uvicorn", ...]` échoue également avec "no such file or directory", ce qui est le plus déroutant.
3.  **Correction des permissions (`chown`) :** L'ajout d'un `chown` pour s'assurer que `appuser` est propriétaire des fichiers n'a pas résolu le problème "not found", ce qui indique un problème de `PATH` ou de copie de fichiers, pas de permissions.
4.  **Approches alternatives d'installation (`pip`, `virtualenv` classique) :** Non testées pour rester fidèle à la stack technique demandée (Poetry).

### Piste la plus probable

Il y a une subtilité dans la manière dont Docker gère la `CMD`, l'utilisateur (`USER`), la copie de fichiers (`COPY --from`) et la variable d'environnement `PATH` qui m'échappe actuellement. L'environnement virtuel semble être correctement copié, mais son contenu n'est pas accessible ou exécutable comme prévu lors de l'étape finale.

Un expert externe devrait se concentrer sur le `backend/Dockerfile` pour identifier la faille dans la logique du build multi-stage. 