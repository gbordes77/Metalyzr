# Metalyzr - Plateforme d'Analyse de Metagame

[![Status](https://img.shields.io/badge/status-en_développement-yellow.svg)](./)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Backend](https://img.shields.io/badge/backend-FastAPI-green.svg)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/frontend-React-blue.svg)](https://reactjs.org)
[![Database](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org)
[![Infra](https://img.shields.io/badge/infra-Docker-blue.svg)](https://www.docker.com)

**Metalyzr** est une plateforme d'analyse du métagame de *Magic: The Gathering*, conçue pour fournir des statistiques détaillées et des visualisations à partir de données de tournois réels.

Le projet a été entièrement refactorisé pour s'appuyer sur une architecture moderne, robuste et scalable.

---

## 🚀 Démarrage Rapide (Méthode Docker)

Le moyen le plus simple et le plus fiable de lancer le projet est d'utiliser Docker et Docker Compose.

### Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Configuration des Identifiants du Scraper

Le pipeline de données repose sur un scraper externe pour collecter les informations des tournois. Pour que celui-ci fonctionne, vous devez fournir des identifiants pour certains sites.

Ouvrez le fichier `docker-compose.yml` et remplacez les valeurs des variables d'environnement suivantes :

```yaml
# In docker-compose.yml, under services.backend.environment
services:
  backend:
    # ...
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/metalyzr
      # ↓↓↓ METTEZ À JOUR CES VALEURS ↓↓↓
      - MELEE_EMAIL=your_email@example.com
      - MELEE_PASSWORD=your_melee_password
      - TOPDECK_API_KEY=your_topdeck_api_key
```

### 2. Lancement des Services

Une fois les identifiants configurés, lancez l'ensemble des services avec une seule commande :

```bash
docker-compose up --build
```

Cette commande va :
1.  Construire l'image Docker pour le backend FastAPI.
2.  Lancer un conteneur pour le backend.
3.  Lancer un conteneur pour la base de données PostgreSQL.
4.  Créer un volume pour la persistance des données de la base de données.

### 3. Initialisation de la Base de Données

Le backend est configuré pour initialiser automatiquement le schéma de la base de données au premier démarrage. Vous devriez voir les logs correspondants dans la sortie de `docker-compose`.

### 4. Lancement du Pipeline de Données

Une fois les services démarrés, vous devez déclencher manuellement la première exécution du pipeline ETL pour peupler la base de données.

Ouvrez un nouveau terminal et exécutez la commande suivante :

```bash
curl -X POST http://localhost:8000/api/metagame/update
```

**Réponse attendue :**
```json
{"message": "Metagame update process started in the background."}
```
Ce processus peut prendre plusieurs minutes, en fonction de la quantité de données à scraper.

---

## 🏗️ Architecture

Le projet est maintenant architecturé autour de services conteneurisés :

```mermaid
graph TD
    subgraph "Infrastructure Docker"
        A[Docker Compose] --> B[Backend Container (FastAPI)];
        A --> C[Database Container (PostgreSQL)];
        B --> C;
    end

    subgraph "Pipeline de Données (ETL)"
        D[Scraper Externe] -- Données brutes --> E[MetagameService];
        E -- Données classifiées --> C;
    end
    
    subgraph "API & Frontend"
        F[Utilisateur/Admin] --> G[Frontend React];
        G -- Requêtes API --> B;
    end

    B --> D;
```

-   **Backend** : Une application **FastAPI** qui sert une API REST pour piloter le pipeline de données et exposer les analyses.
-   **Base de Données** : Une instance **PostgreSQL** qui stocke toutes les données de manière structurée (tournois, decks, cartes, etc.).
-   **Scraper** : Le projet `fbettega/mtg_decklist_scrapper` est intégré en tant que sous-module Git et est orchestré par le backend pour l'acquisition de données.
-   **Frontend** : Une application **React** (non incluse dans le Docker Compose pour l'instant) qui consommera l'API pour afficher les visualisations et fournir les outils d'administration.

---

## 🛠️ Endpoints de l'API Principale

L'API est accessible sur `http://localhost:8000`.

-   `POST /api/metagame/update`
    -   Déclenche une mise à jour en arrière-plan des données du métagame.
-   `GET /api/metagame/status`
    -   Retourne le statut du `MetagameService` et de ses composants (scraper, base de données).
-   `GET /api/metagame/analysis/metagame_share/{format_name}`
    -   Calcule et retourne la répartition en pourcentage des archétypes pour un format donné.
    -   *Exemple :* `/api/metagame/analysis/metagame_share/Modern?days=14`

---

## 📚 Documentation Complémentaire

-   **[Architecture Technique](./ARCHITECTURE.md)** : Détails sur la structure du code, le schéma de la base de données et le flux de données.

(Les autres documents de l'ancien système ont été archivés pour éviter toute confusion).
