# État des Lieux - Metalyzr (10 Juillet 2024)

## Contexte et Objectif

La mission est de rendre le projet Metalyzr, initialement dans un état de chaos organisationnel, pleinement opérationnel. Après une restructuration majeure (dépendances, Docker, base de données, CI/CD), un obstacle majeur a été rencontré.

## Problème Majeur Rencontré

Le build de l'image Docker du backend échoue systématiquement sur l'environnement de l'utilisateur (macOS ARM64) à l'étape `poetry install`. Malgré de multiples corrections du `Dockerfile` et des tentatives de purges de cache, le problème persiste, indiquant un souci d'environnement local profond lié à Docker Desktop sur ARM64.

## Pivot Stratégique : Exécution Locale

Pour contourner ce blocage et valider l'architecture applicative (base de données, API, collecteurs de données), la décision a été prise de pivoter vers une exécution locale du backend, en abandonnant temporairement son lancement via Docker.

**Actions Réalisées :**
1.  **Simplification de Docker Compose :** Le fichier `docker-compose.yml` a été modifié pour ne plus gérer que le lancement des services tiers stables : `db` (PostgreSQL) et `redis`.
2.  **Création d'un Script de Lancement Local :** Un script `start_backend_local.sh` a été créé. Il automatise :
    *   La création d'un environnement virtuel Python (`backend/.venv_local`).
    *   L'installation des dépendances du projet via `poetry install`.
    *   Le lancement du serveur FastAPI avec `uvicorn`.
3.  **Correction d'Erreurs de Démarrage :**
    *   Une première `ImportError` concernant `Base` de SQLAlchemy a été corrigée dans `backend/database.py`.
    *   Le dernier log a montré une nouvelle erreur de `traceback` au moment de la connexion à la base de données. Le débogage était en cours lorsque la session a été interrompue.

## État Actuel

- Le code est dans un état où le backend **devrait** pouvoir se lancer localement.
- Les services `db` et `redis` sont prêts à être lancés via `docker-compose`.
- Le frontend n'a pas encore été traité et sera la prochaine étape une fois le backend validé.

## Prochaines Étapes Immédiates

1.  **Lancer les services de base (dans un terminal) :**
    ```bash
    docker-compose up
    ```
2.  **Lancer le backend (dans un second terminal) :**
    ```bash
    ./start_backend_local.sh
    ```
3.  **Analyser le traceback :** Le script s'arrêtera probablement sur l'erreur de connexion à la base de données. Il faudra l'analyser pour la résoudre (probablement un problème avec `psycopg2` ou la chaîne de connexion).
4.  **Valider l'API :** Une fois le serveur démarré, tester l'endpoint [http://localhost:8000/api/v1/tournaments_from_api](http://localhost:8000/api/v1/tournaments_from_api). 