# Metalyzr - Guide Technique Approfondi

Ce document fournit une analyse détaillée de l'architecture, de la structure du code et des configurations du projet Metalyzr. Il est destiné à des experts techniques ayant une bonne connaissance de Docker, Python (FastAPI), et React.

## 1. Philosophie d'Architecture

L'objectif est de créer un environnement de développement local complet, reproductible et aussi proche que possible d'un environnement de production "cloud-native".

- **Containerisation Totale :** Chaque service (backend, frontend, BDD, cache) est isolé dans son propre conteneur Docker.
- **Orchestration avec Compose :** `docker-compose.yml` définit l'ensemble des services, leurs relations, les ports exposés et les volumes pour le développement.
- **Builds Multi-Stage :** Les `Dockerfiles` utilisent des builds en plusieurs étapes pour créer des images finales légères, sécurisées et optimisées, en séparant les dépendances de build du runtime final.
- **Configuration Découplée :** La configuration est gérée via des fichiers (`nginx.conf`) et des variables d'environnement (`docker-compose.yml`) plutôt qu'en dur dans le code.

## 2. Structure du Projet

```
Metalyzr/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py        # Point d'entrée FastAPI
│   │   ├── crud.py        # Fonctions CRUD (Create, Read, Update, Delete)
│   │   ├── models.py      # Modèles de données Pydantic
│   │   └── services.py    # Logique métier
│   ├── Dockerfile         # Instructions de build pour le backend
│   └── pyproject.toml     # Dépendances et métadonnées Python (Poetry)
│
├── frontend/
│   ├── public/
│   │   └── index.html     # Template HTML de base pour React
│   ├── src/
│   │   ├── components/    # Composants React réutilisables (ex: ui/card.tsx)
│   │   ├── pages/         # Vues principales (AdminDashboard, PublicDashboard)
│   │   ├── App.tsx        # Composant React racine
│   │   ├── index.tsx      # Point d'entrée de l'application React
│   │   └── tailwind.css   # Styles de base Tailwind
│   ├── Dockerfile         # Instructions de build pour le frontend
│   ├── package.json       # Dépendances et scripts Node.js
│   ├── tailwind.config.js # Configuration de Tailwind CSS
│   └── tsconfig.json      # Configuration de TypeScript
│
├── data/                    # (Prévu) Datasets bruts et traités
├── docs/                    # Documentation utilisateur et projet
├── infra/
│   └── docker/
│       └── postgres/
│           └── init.sql   # Script d'initialisation de la BDD
├── scripts/                 # (Prévu) Scripts d'automatisation
├── tests/                   # (Prévu) Tests unitaires et d'intégration
│
├── .gitignore
├── docker-compose.yml       # Fichier d'orchestration des services
└── README.md
```

## 3. Analyse des Composants Clés

### 3.1. `docker-compose.yml`

- **Services :** Définit 4 services : `postgres`, `redis`, `backend`, `frontend`.
- **Backend :**
  - Contexte de build : `./backend`.
  - Dockerfile : `backend/Dockerfile`.
  - Ports : Mappe le port `8000` du conteneur au port `8000` de l'hôte.
  - Dépendances : Dépend explicitement de `postgres` et `redis` pour s'assurer qu'ils démarrent avant.
- **Frontend :**
  - Contexte de build : `./frontend`.
  - Dockerfile : `frontend/Dockerfile`.
  - Ports : Mappe le port `3000` du conteneur au port `3000` de l'hôte.
- **Postgres :**
  - Image : `postgres:16-alpine`.
  - Volumes : Utilise un volume nommé `postgres_data` pour la persistance des données.
  - Healthcheck : Intègre une vérification pour s'assurer que la base de données est prête à accepter des connexions avant que le backend ne démarre.
- **Redis :**
  - Image : `redis:7-alpine`.

### 3.2. `backend/Dockerfile`

C'est le fichier qui pose problème, mais voici sa structure cible :
- **Stage `builder` :**
  1. Part d'une image `python:3.11-slim`.
  2. Installe `Poetry`.
  3. Configure Poetry pour créer un environnement virtuel **dans le projet** (`.venv`). C'est un point crucial.
  4. Copie `pyproject.toml` et `poetry.lock`.
  5. Lance `poetry install` pour télécharger et installer les dépendances dans `./.venv`.
- **Stage Final :**
  1. Part d'une image `python:3.11-slim` propre et légère.
  2. Copie l'environnement virtuel complet (`--from=builder /app/.venv`) du stage précédent.
  3. Copie le code source de l'application.
  4. Ajoute le `bin` de l'environnement virtuel au `$PATH` de l'image.
  5. Crée un utilisateur non-root `appuser` pour des raisons de sécurité.
  6. Transfère la propriété des fichiers à `appuser`.
  7. Lance `uvicorn` via la `CMD`.

### 3.3. `frontend/Dockerfile`

- **Stage `builder` :**
  1. Part d'une image `node:18-alpine`.
  2. Copie `package.json` et installe les dépendances avec `npm install`.
  3. Copie le reste du code source.
  4. Lance `npm run build` pour créer une version de production statique optimisée dans `/app/build`.
- **Stage Final :**
  1. Part d'une image `nginx:1.25-alpine` ultra-légère.
  2. Copie les fichiers statiques depuis le stage `builder` dans le dossier servi par Nginx.
  3. Copie une configuration Nginx personnalisée (`nginx.conf`) pour bien gérer le routage de l'application React.
  4. Expose le port 80.

## 4. Intégrations et Code

- **Backend (FastAPI) :** Le code fourni dans `backend/app/` met en place une API REST basique avec des modèles Pydantic pour la validation des données.
- **Frontend (React/TypeScript) :** Le code dans `frontend/src/` utilise TypeScript et des composants fonctionnels. Il intègre des placeholders pour la librairie de composants `shadcn/ui` et des icônes `lucide-react`. La structure est prête à consommer l'API du backend.
- **Styling (Tailwind CSS) :** La configuration de base de Tailwind est prête. Les classes utilitaires sont utilisées dans les composants React pour le style.
- **Base de Données (PostgreSQL) :** Le service est configuré et un script `init.sql` est prêt à être utilisé pour initialiser le schéma de la base de données au premier démarrage.

Ce guide représente l'état cible et fonctionnel de l'infrastructure que j'ai tenté de mettre en place. 