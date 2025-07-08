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

## CI/CD Pipeline

### GitHub Actions Architecture

```mermaid
graph TB
    A[Push/PR] --> B[Checkout Code]
    B --> C[Setup Python Matrix]
    B --> D[Setup Node.js]
    C --> E[Backend Tests]
    D --> F[Frontend Tests] 
    E --> G[Integration Tests]
    F --> G
    G --> H[Docker Build Test]
    H --> I[Deploy Ready]
```

### Workflow configuration
```yaml
# .github/workflows/ci.yml
- Matrix testing: Python 3.8, 3.9, 3.10, 3.11
- Parallel jobs: Backend, Frontend, Integration, Docker
- Caching: pip dependencies, npm packages
- Linting: flake8, ESLint, TypeScript
- Testing: pytest, Jest, health checks
```

### Pre-commit Hooks
```bash
# Installation
pip install pre-commit
pre-commit install

# Hooks actifs
- black (Python formatting)
- isort (import sorting) 
- flake8 (Python linting)
- bandit (security scanning)
- eslint (JavaScript/TypeScript)
```

## Health Checks et Monitoring

### Architecture Health Checker

```python
# backend/health_enhanced.py
class HealthChecker:
    - check_database_connection()     # PostgreSQL status
    - check_redis_connection()        # Redis availability  
    - check_melee_api()              # API externe Melee.gg
    - check_mtgtop8_availability()   # Source de scraping
    - check_mtgo_cache_repo()        # Repository GitHub
    - get_system_metrics()           # CPU/RAM/Disk usage
    - comprehensive_health_check()   # Orchestration complète
```

### Endpoints de monitoring

| Endpoint | Description | Cache TTL |
|----------|-------------|-----------|
| `/health` | Health check basique | Aucun |
| `/health/detailed` | Diagnostics complets | 30s |
| `/metrics` | Métriques Prometheus | Aucun |
| `/api/cache/status` | Status cache MTGODecklistCache | 60s |

### Métriques Prometheus

```python
# Métriques exposées automatiquement
REQUEST_COUNT = Counter('metalyzr_requests_total')
REQUEST_DURATION = Histogram('metalyzr_request_duration_seconds') 
CACHE_HITS = Counter('metalyzr_cache_hits_total')
API_ERRORS = Counter('metalyzr_api_errors_total')
```

### Réponse health check détaillé

```json
{
  "status": "healthy|degraded|unhealthy",
  "check_duration_ms": 245.8,
  "services": {
    "database": {"status": "healthy", "response_time_ms": 5.2},
    "redis": {"status": "healthy", "response_time_ms": 3.1},
    "melee_api": {"status": "healthy", "response_time_ms": 156.7},
    "mtgtop8": {"status": "healthy", "response_time_ms": 89.4},
    "mtgo_cache_repo": {"status": "healthy", "response_time_ms": 112.3}
  },
  "system_metrics": {
    "memory": {"used_mb": 257.4, "percent": 12.8},
    "cpu_percent": 8.5,
    "uptime_minutes": 1440.2
  }
}
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