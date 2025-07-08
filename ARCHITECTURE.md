# Metalyzr - Architecture Technique

## Vue d'ensemble

Application d'analyse du métagame Magic: The Gathering avec collecte automatisée des données de tournois.

### Stack technique
- **Backend:** FastAPI, Python 3.11, SQLAlchemy, Pydantic
- **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts
- **Base de données:** PostgreSQL 15
- **Cache:** Redis 7
- **Containerisation:** Docker, Docker Compose

## Architecture système

```
Frontend (React) → API (FastAPI) → Database (PostgreSQL)
                                 → Cache (Redis)
                                 → Scraper (Python)
```

### Services Docker

```yaml
services:
  backend:          # FastAPI + Python
  postgres:         # Base de données principale
  redis:           # Cache et sessions
  scraper:         # Collecteur de données
  frontend:        # Interface React (développement)
```

## Backend FastAPI

### Structure
```
backend/
├── main.py              # Point d'entrée FastAPI
├── api/                 # Endpoints REST
│   ├── tournaments.py   # API tournois
│   ├── archetypes.py    # API archétypes
│   └── admin/           # API administration
├── models/              # Modèles SQLAlchemy
│   ├── tournament.py
│   ├── deck.py
│   └── archetype.py
├── services/            # Logique métier
└── database.py          # Configuration DB
```

### Endpoints principaux
```
GET /health                    # Santé du système
GET /api/tournaments           # Liste des tournois
GET /api/archetypes           # Liste des archétypes
POST /api/init-sample-data     # Initialiser données d'exemple
```

## Base de données PostgreSQL

### Schéma principal
```sql
CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    format VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(255),
    total_players INTEGER
);

CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    format VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    color_identity VARCHAR(20)
);

CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    archetype_id INTEGER REFERENCES archetypes(id),
    player_name VARCHAR(255),
    position INTEGER,
    wins INTEGER,
    losses INTEGER
);
```

## Scraper

### Architecture
```
scraper/
├── main.py              # Point d'entrée
├── mtgtop8_scraper.py   # Scraper MTGTop8
├── base_scraper.py      # Interface commune
├── config.py           # Configuration
└── models.py           # Modèles de données
```

### Configuration
```python
SCRAPER_DELAY = 2.0                    # Délai entre requêtes
MAX_TOURNAMENTS_PER_RUN = 50           # Limite par exécution
TIMEOUT_SECONDS = 30                   # Timeout HTTP
```

## Frontend React

### Structure
```
frontend/
├── src/
│   ├── components/         # Composants réutilisables
│   │   ├── ui/            # Composants UI de base
│   │   └── charts/        # Graphiques
│   ├── pages/             # Pages principales
│   │   ├── public/        # Dashboard public
│   │   └── admin/         # Interface admin
│   ├── hooks/             # Hooks personnalisés
│   ├── services/          # Client API
│   └── utils/             # Utilitaires
```

### Pages disponibles
- `/` - Dashboard public
- `/admin` - Interface d'administration
- `/tournaments/:id` - Détails tournoi

## Configuration

### Variables d'environnement
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost/metalyzr
REDIS_URL=redis://localhost:6379

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Scraper
SCRAPER_DELAY=2.0
MAX_TOURNAMENTS_PER_RUN=50
```

## Déploiement

### Docker Compose
```bash
# Démarrer tous les services
docker-compose up -d

# Initialiser la base de données
docker exec -it metalyzr-backend-1 python init_db.py

# Vérifier l'état
docker-compose ps
```

### Accès aux services
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Base de données: localhost:5432

## Développement

### Setup local
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Tests
```bash
# Backend
python -m pytest

# Frontend
npm test
```

## Monitoring

### Logs
```bash
# Logs backend
docker logs metalyzr-backend-1

# Logs scraper
docker logs metalyzr-scraper-1

# Logs base de données
docker logs metalyzr_postgres
```

### Diagnostic
```bash
# Santé de l'API
curl http://localhost:8000/health

# État des conteneurs
docker-compose ps

# Connexion DB
docker exec -it metalyzr_postgres psql -U metalyzr -d metalyzr
```

## Sauvegarde

### Base de données
```bash
# Export
docker exec -t metalyzr_postgres pg_dump -U metalyzr metalyzr > backup.sql

# Import
docker exec -i metalyzr_postgres psql -U metalyzr metalyzr < backup.sql
```

## Résolution de problèmes

### Erreurs communes
1. **Port déjà utilisé:** Vérifier avec `lsof -i :8000`
2. **DB connection failed:** Vérifier PostgreSQL avec `docker logs`
3. **Frontend ne charge pas:** Vérifier CORS et variables d'environnement
4. **Scraper timeout:** Ajuster `TIMEOUT_SECONDS` et `SCRAPER_DELAY`

### Commandes utiles
```bash
# Redémarrer un service
docker-compose restart backend

# Nettoyer volumes
docker-compose down -v

# Rebuild complet
docker-compose build --no-cache
``` 