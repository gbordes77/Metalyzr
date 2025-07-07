# Guide de Passation du Projet Metalyzr

## 1. Contexte et Objectif du Projet

**Metalyzr** est une application conçue pour agréger et analyser des données de métagame de tournois de jeux de cartes (ex: Magic: The Gathering).

L'architecture cible est composée de plusieurs services :
*   Un **Scraper** (`scraper/`) pour collecter les données depuis différentes sources web.
*   Un **Backend** (`backend/`) en FastAPI pour traiter et exposer ces données via une API REST.
*   Une **Base de données** (PostgreSQL) pour le stockage persistant.
*   Un **Cache/Queue** (Redis) pour les tâches asynchrones et la mise en cache.
*   Un **Dashboard** (`frontend/`) en React/Next.js pour la visualisation des données.

L'ensemble de l'environnement est conçu pour être orchestré par Docker et Docker Compose.

## 2. État Actuel du Projet

Le projet est à ses débuts. La structure de base des répertoires est en place, ainsi que les fichiers de configuration initiaux pour Docker.

*   `docker-compose.yml`: Définit les services `backend`, `frontend`, `postgres` et `redis`.
*   `backend/Dockerfile`: Un Dockerfile multi-stage a été mis en place pour construire une image de production optimisée pour le service FastAPI.
*   Les autres services ont des Dockerfiles de base.
*   Un premier état des lieux (`STATUS_REPORT.md`) a été rédigé au cours du débogage.

**Aucun code fonctionnel (scraping, API, UI) n'a encore été développé.** Le travail s'est entièrement concentré sur la mise en place de l'infrastructure de développement Docker.

## 3. Le Problème Bloquant (Spécifique à l'Environnement)

**Le point le plus critique de cette passation est un problème non résolu sur la machine du développeur initial (macOS, Apple Silicon).**

*   **Symptôme :** Le conteneur du `backend` refuse de démarrer avec une erreur `OCI runtime create failed ... no such file or directory: unknown`.
*   **Diagnostic :** Après des investigations approfondies (détaillées dans `STATUS_REPORT.md`), nous avons la certitude que **le problème ne vient PAS du code ou de la configuration du projet**, mais d'un bug de bas niveau dans l'installation de Docker Desktop sur la machine en question. L'erreur persiste même en essayant d'exécuter un binaire Python de base, ce qui est très anormal.

## 4. Recommandations pour la Nouvelle Équipe

### Étape 1 : Tenter de Lancer l'Environnement Docker
La première chose à faire sur une nouvelle machine est de cloner le dépôt et de tenter de lancer l'environnement :
```bash
docker-compose up --build
```
Il est **très probable que cela fonctionne directement** sur une machine avec une installation saine de Docker.

### Étape 2 : Si le Problème Persiste (sur macOS/Apple Silicon)
Si vous rencontrez la même erreur `OCI runtime ... no such file or directory`, cela confirme un problème avec votre installation locale de Docker.

Un expert externe a fourni une analyse et un **script de réparation complet** :
*   **Fichier :** `scripts/docker-fix-macos-m1.sh`
*   **Objectif :** Ce script effectue une désinstallation complète et agressive de Docker, nettoie tous les fichiers résiduels, et réinstalle proprement la dernière version avec une configuration optimisée.
*   **Utilisation :**
    ```bash
    # À lancer depuis la racine du projet
    sudo ./scripts/docker-fix-macos-m1.sh
    ```
    (L'utilisation de `sudo` est impérative pour qu'il puisse nettoyer les fichiers système).
    **Un redémarrage complet du Mac est essentiel après l'exécution du script.**

### Étape 3 : Plan de Contournement (Développement Local sans Docker)
Si la réparation de Docker s'avère impossible ou trop longue, un plan détaillé a été fourni par l'expert pour mettre en place un **environnement de développement entièrement local**, sans Docker. Ce plan est très complet et se trouve dans les logs de la conversation qui a mené à cette passation. Il inclut :
*   L'installation de PostgreSQL et Redis via Homebrew.
*   La configuration des environnements Python et Node.js.
*   Les variables d'environnement et les commandes de lancement pour chaque service.

**Priorité :** La priorité doit être de faire fonctionner l'environnement Docker, qui est la cible de production. Le plan de contournement est une solution de repli pour ne pas bloquer le développement applicatif.

## 5. Prochaines Étapes de Développement (Une fois l'infra fonctionnelle)

1.  **Développer le Scraper :** Implémenter la logique de collecte de données pour le premier site source.
2.  **Développer l'API Backend :** Créer les premiers endpoints pour stocker et récupérer les données.
3.  **Développer le Dashboard :** Mettre en place les premières visualisations.
4.  **Améliorer le `docker-compose.yml` :** Intégrer les `healthchecks` et les bonnes pratiques de la version 3.8, comme suggéré dans l'analyse de l'expert. 