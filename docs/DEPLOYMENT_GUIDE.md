# Guide de Déploiement - Metalyzr

Ce document décrit l'architecture technique de Metalyzr et fournit les instructions pour déployer l'environnement de développement local.

## 1. Architecture Technique

Metalyzr est basé sur une architecture de microservices conteneurisée avec Docker, conçue pour être scalable et maintenable.

- **Frontend** : Une application Single Page Application (SPA) construite avec **React** et **TypeScript**. Elle est servie par un serveur **Nginx** léger en production.
- **Backend** : Une API RESTful développée avec **FastAPI** (Python). Elle gère toute la logique métier, les interactions avec la base de données et le traitement des données.
- **Base de Données** : Une instance **PostgreSQL** est utilisée pour le stockage persistant des données (tournois, decks, archétypes, etc.).
- **File d'attente (Queue)** : **Redis** est utilisé comme message broker pour gérer les tâches asynchrones, notamment le scraping et le pipeline ETL.

L'ensemble des services est orchestré par **Docker Compose** pour l'environnement de développement local.

![Architecture Diagram](https://i.imgur.com/example.png) <!-- Placeholder -->

## 2. Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre machine :
- Docker (`>= 20.10`)
- Docker Compose (`>= 1.29`)

## 3. Installation et Lancement (Développement Local)

Suivez ces étapes pour lancer Metalyzr sur votre machine.

### a. Cloner le Repository
Clonez le projet depuis GitHub :
```bash
git clone https://github.com/gbordes77/Metalyzr.git
cd Metalyzr
```

### b. Configuration de l'Environnement
Le projet utilise des variables d'environnement pour configurer les services. Un fichier d'exemple est fourni.
1.  Copiez le fichier d'exemple :
    ```bash
    cp .env.example .env
    ```
2.  Ouvrez le fichier `.env` et personnalisez les valeurs si nécessaire (clés API, etc.). Les valeurs par défaut sont conçues pour fonctionner directement en local.

### c. Lancer les Services
Utilisez Docker Compose pour construire les images et démarrer tous les conteneurs :
```bash
docker-compose up -d --build
```
- `-d` : Lance les conteneurs en mode détaché (en arrière-plan).
- `--build` : Force la reconstruction des images Docker si des changements ont été faits (par exemple dans un `Dockerfile`).

### d. Accéder aux Services
Une fois les conteneurs démarrés, vous pouvez accéder aux différents services :

- **Frontend (Application Publique)** : [http://localhost:3000](http://localhost:3000)
- **Backend (API)** : [http://localhost:8000](http://localhost:8000)
- **Documentation de l'API (Swagger UI)** : [http://localhost:8000/docs](http://localhost:8000/docs)

## 4. Gestion des Services

- **Voir les logs** :
  ```bash
  docker-compose logs -f [nom_du_service]
  # Exemple: docker-compose logs -f backend
  ```
- **Arrêter les services** :
  ```bash
  docker-compose down
  ```
- **Exécuter une commande dans un conteneur** :
  ```bash
  docker-compose exec [nom_du_service] [commande]
  # Exemple (lancer une session shell dans le backend):
  # docker-compose exec backend /bin/bash
  ```

## 5. Déploiement en Production (Concept)

Le déploiement en production (non couvert par ce setup initial) est prévu pour utiliser une infrastructure cloud-native :
- **Conteneurisation** : Les images Docker construites localement sont la base du déploiement.
- **Orchestration** : **Kubernetes** sera utilisé pour gérer les conteneurs en production, assurant la haute disponibilité et la scalabilité.
- **Infrastructure as Code (IaC)** : **Terraform** sera utilisé pour provisionner et gérer l'infrastructure cloud.
- **CI/CD** : Un pipeline **GitHub Actions** automatisera les tests, la construction des images Docker et le déploiement sur Kubernetes via une approche GitOps (avec ArgoCD). 