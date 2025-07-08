# Metalyzr

Plateforme d'analyse du métagame Magic: The Gathering qui collecte et analyse les données de tournois.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![React](https://img.shields.io/badge/react-18.0%2B-blue)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104%2B-green)](https://fastapi.tiangolo.com)

## Démarrage rapide

```bash
git clone https://github.com/gbordes77/Metalyzr.git && cd Metalyzr
cd backend && python -m venv venv_simple && source venv_simple/bin/activate && pip install fastapi uvicorn python-multipart
cd ../frontend && npm install && npm run build
cd ../backend && python main_simple.py &
cd ../frontend/build && node serve-spa.js
# Dashboard: http://localhost:3000 - API: http://localhost:8000
```

## Fonctionnalités

### Actuellement implémentées
- API REST FastAPI avec endpoints pour tournois et archétypes
- Dashboard React avec visualisations des données
- Classification d'archétypes avec engine Badaro
- Client API pour Melee.gg
- Interface d'administration
- Système de cache simple

### Sources de données
- **Melee.gg API** : Source principale pour données temps réel
- **MTGODecklistCache** : Cache structuré maintenu par Jiliac
- **MTGTop8 Scraping** : Backup et données historiques étendues

## Architecture

### Stack technologique

```mermaid
graph TB
    subgraph "Frontend"
        A[React 18] --> B[TypeScript]
        B --> C[Tailwind CSS]
        C --> D[Recharts]
    end
    
    subgraph "Backend"
        E[FastAPI] --> F[Python 3.8+]
        F --> G[Pydantic]
        G --> H[Uvicorn]
    end
    
    subgraph "Scraping & Classification"
        I[Scrapy] --> J[Badaro Engine]
        J --> K[Melee API Client]
        K --> L[MTGODecklistCache]
    end
    
    subgraph "Data Sources"
        M[Melee.gg API]
        N[MTGTop8.com]
        O[MTGO.com]
        P[MTGODecklistCache Repo]
    end
    
    A --> E
    E --> I
    I --> M
    I --> N
    I --> O
    L --> P
```

### Composants principaux

| Composant | Technologie | Rôle | Statut |
|-----------|-------------|------|--------|
| Frontend | React + TypeScript | Interface utilisateur | ✅ Fonctionnel |
| Backend | FastAPI + Python | API REST & logique métier | ✅ Fonctionnel |
| Badaro Engine | Python | Classification archétypes | ✅ Intégré |
| Melee Client | Python + aiohttp | API Melee.gg temps réel | ✅ Implémenté |
| MTGTop8 Scraper | Scrapy | Scraping backup | 🔄 En cours |
| Cache Manager | Python + Git | Gestion MTGODecklistCache | 🔄 En cours |
| Admin Interface | React | Configuration système | ✅ Fonctionnel |

## Installation

### Prérequis
- Python 3.8+ avec pip
- Node.js 16+ avec npm/yarn
- Git pour clonage et gestion cache

### Installation Express

```bash
# 1. Cloner le repository
git clone https://github.com/gbordes77/Metalyzr.git
cd Metalyzr

# 2. Backend Setup
cd backend
python -m venv venv_simple
source venv_simple/bin/activate  # Windows: venv_simple\Scripts\activate
pip install fastapi uvicorn python-multipart

# 3. Frontend Setup  
cd ../frontend
npm install
npm run build

# 4. Démarrage Backend
cd ../backend
source venv_simple/bin/activate
python main_simple.py

# 5. Démarrage Frontend (nouveau terminal)
cd frontend/build
node serve-spa.js

# 6. Accès Application
# Dashboard: http://localhost:3000
# Admin: http://localhost:3000/admin  
# API: http://localhost:8000
```

### Installation Docker (Alternative)

```bash
# Démarrage complet avec Docker Compose
docker-compose up -d

# Accès aux services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Guide d'Utilisation

### Dashboard Principal

Le dashboard offre une vue d'ensemble du méta :

1. **Vue Méta Globale**
   - Répartition des archétypes
   - Graphiques de popularité et performance
   - Filtres par format, période, source

2. **Analyse d'Archétypes**
   - Détail par archétype avec sous-variantes
   - Tendances de popularité historique
   - Win rate et performance moyenne

3. **Tournois Récents**
   - Liste des derniers événements
   - Résultats détaillés avec decklists
   - Liens vers sources externes

### Interface Admin

L'interface admin permet la configuration avancée :

1. **Configuration Sources**
   - Priorisation API vs Scraping
   - Fréquence de mise à jour
   - Tokens API et authentification

2. **Gestion Archétypes**
   - Règles de classification personnalisées
   - Seuils de confiance
   - Mapping archétype-couleurs

3. **Monitoring Système**
   - Statistiques de performance
   - Logs d'erreurs et debugging
   - Métriques de qualité données

### API REST

L'API publique expose toutes les fonctionnalités :

```bash
# Health checks
GET /health                    # Status basique
GET /health/detailed          # Monitoring complet avec services externes

# Monitoring
GET /metrics                  # Métriques Prometheus

# Statistiques
GET /api/stats               # Statistiques globales

# Tournois  
GET /api/tournaments         # Liste des tournois
GET /api/tournaments/{id}    # Détails tournoi spécifique
POST /api/tournaments        # Créer tournoi

# Archétypes
GET /api/archetypes          # Liste des archétypes
POST /api/archetypes         # Créer archétype

# Cache
GET /api/cache/status        # Status du cache MTGODecklistCache
POST /api/cache/sync         # Forcer synchronisation cache

# Développement
GET /api/init-sample-data    # Initialiser données d'exemple
```

Documentation complète : http://localhost:8000/docs

## Classification d'Archétypes Badaro

### Architecture du Moteur

Le moteur Badaro est inspiré du [MTGOArchetypeParser](https://github.com/Badaro/MTGOArchetypeParser) :

```python
# Exemple de règle d'archétype Burn
{
  "name": "Burn",
  "conditions": [
    {"type": "InMainboard", "cards": ["Lightning Bolt"]},
    {"type": "InMainboard", "cards": ["Goblin Guide"]},
    {"type": "OneOrMoreInMainboard", "cards": ["Monastery Swiftspear", "Eidolon of the Great Revel"]}
  ],
  "variants": {
    "Boros Burn": {
      "conditions": [{"type": "InMainboard", "cards": ["Boros Charm"]}]
    }
  }
}
```

### Types de Conditions Supportées

| Condition | Description | Exemple |
|-----------|-------------|---------|
| `InMainboard` | Carte obligatoire en main | Lightning Bolt pour Burn |
| `OneOrMoreInMainboard` | Au moins une des cartes | Bolt ou Spike pour Burn |
| `TwoOrMoreInMainboard` | Au moins deux des cartes | 2+ rituels pour Belcher |
| `DoesNotContain` | Carte interdite | Pas de créatures pour Control |

### Système de Fallbacks

Pour les decks "goodstuff" sans cartes signature :

```python
# Exemple Control fallback
{
  "name": "Control",
  "common_cards": [
    "Cryptic Command", "Supreme Verdict", "Teferi, Hero of Dominaria",
    "Snapcaster Mage", "Celestial Colonnade", "Mana Leak"
  ],
  "threshold": 0.1  # 10% des cartes communes minimum
}
```

### Niveaux de Confiance

- **HIGH (90%+)** : Match exact archétype + variante
- **MEDIUM (70-89%)** : Match archétype principal
- **LOW (50-69%)** : Match fallback avec bonne couverture
- **UNKNOWN (<50%)** : Classification par couleur ou échec

## Sources de Données

### Melee.gg API (Priorité #1)

Source principale pour données temps réel :

```python
# Configuration API Melee
MELEE_CONFIG = {
    "base_url": "https://api.melee.gg/v1",
    "rate_limit": "60/minute",
    "priority": 70,  # 70% du trafic
    "formats_supported": ["Modern", "Standard", "Pioneer", "Legacy"]
}
```

**Avantages** :
- Données temps réel (< 1h délai)
- API structurée et fiable
- Métadonnées complètes (joueurs, rounds, standings)
- Authentification token disponible

### MTGODecklistCache (Backbone)

Cache structuré maintenu par [Jiliac](https://github.com/Jiliac/MTGODecklistCache) :

```python
# Structure cache MTGODecklistCache
{
  "tournament": {
    "name": "Modern Preliminary",
    "date": "2025-01-08",
    "format": "Modern",
    "source": "mtgo.com"
  },
  "decks": [
    {
      "player": "PlayerName",
      "position": "4-0",
      "archetype": "Burn",  # Pré-classifié
      "mainboard": {"Lightning Bolt": 4, ...},
      "sideboard": {"Deflecting Palm": 2, ...}
    }
  ]
}
```

**Avantages** :
- Historique complet avec commits réguliers
- Mise à jour quotidienne 17:00 UTC
- Format normalisé JSON structuré
- Maintenance active par Jiliac

### MTGTop8 Scraping (Backup)

Scraper Scrapy pour robustesse :

```python
# Configuration MTGTop8 Scraper
class MTGTop8Spider(scrapy.Spider):
    name = "mtgtop8"
    start_urls = ["https://mtgtop8.com/format?f=MO"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Respectueux
        'CONCURRENT_REQUESTS': 1,
        'ROBOTSTXT_OBEY': True
    }
```

**Usage** :
- Backup si API indisponible
- Données historiques étendues
- Vérification croisée qualité
- Source de référence établie

## Pipeline de Traitement

### Workflow Global

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant M as Melee API
    participant C as Cache MTGODecklistCache
    participant B as Badaro Engine
    participant D as Database
    participant F as Frontend

    S->>M: Fetch latest tournaments
    M->>S: Tournament data
    S->>C: Pull cache updates
    C->>S: Historical data
    S->>B: Classify all decks
    B->>S: Archetype results
    S->>D: Store processed data
    D->>F: Real-time updates
```

### Traitement Temps Réel

1. **Récupération** : API Melee.gg toutes les heures
2. **Enrichissement** : Cache MTGODecklistCache quotidien
3. **Classification** : Engine Badaro pour tous les decks
4. **Validation** : Contrôles qualité et cohérence
5. **Stockage** : Base de données avec historique
6. **Diffusion** : WebSocket pour mise à jour live

### Gestion d'Erreurs

```python
# Stratégie de fallback robuste
ERROR_HANDLING = {
    "api_timeout": "fallback_to_cache",
    "rate_limit": "exponential_backoff", 
    "classification_failure": "color_fallback",
    "data_corruption": "rollback_last_known_good"
}
```

## Interface Utilisateur

### Dashboard React

Interface moderne construite avec :

- **React 18** : Framework principal
- **TypeScript** : Type safety et intellisense
- **Tailwind CSS** : Styling utilitaire moderne
- **Recharts** : Graphiques interactifs
- **React Router** : Navigation SPA

### Design Responsive

```css
/* Breakpoints adaptatifs */
.dashboard-grid {
  grid-template-columns: 1fr;
  
  @media (md) {
    grid-template-columns: 1fr 1fr;
  }
  
  @media (lg) {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
```

### Système de Design

- **Couleurs** : Palette MTG officielle (bleu/blanc/noir)
- **Typography** : Inter + monospace pour code
- **Composants** : Library réutilisable
- **Accessibilité** : WCAG 2.1 AA compliant

## Configuration Avancée

### Variables d'Environnement

```bash
# .env configuration
MELEE_API_TOKEN=your_token_here
MTGO_CACHE_PATH=./cache/mtgo_data
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
SCRAPING_RATE_LIMIT=60  # requests per minute
DATABASE_URL=postgresql://user:pass@localhost/metalyzr
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Configuration Monitoring

```yaml
# monitoring.yml
metrics:
  collection_interval: 60s
  retention_period: 30d
  
alerts:
  api_error_rate: 
    threshold: 5%
    notification: slack
  
  classification_accuracy:
    threshold: 90%
    notification: email
```

### Configuration Cache

```python
# Cache strategy configuration
CACHE_CONFIG = {
    "mtgo_data": {
        "ttl": 3600,  # 1 hour
        "strategy": "write_through"
    },
    "archetype_rules": {
        "ttl": 86400,  # 24 hours  
        "strategy": "write_behind"
    },
    "api_responses": {
        "ttl": 300,  # 5 minutes
        "strategy": "write_around"
    }
}
```

## CI/CD et Qualité

### Pipeline GitHub Actions

Pipeline automatisé pour garantir la qualité :

```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on: [push, pull_request]

jobs:
  test-backend:
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    steps:
      - name: Install dependencies
        run: pip install -r requirements_simple.txt
      - name: Lint with flake8
        run: flake8 backend --count --statistics
      - name: Test with pytest
        run: python -m pytest -v
      - name: Health check test
        run: curl -f http://localhost:8000/health
```

**Features** :
- Tests multi-versions Python (3.8 à 3.11)
- Linting automatique avec flake8
- Tests d'intégration frontend/backend
- Validation Docker builds
- Cache NPM et pip pour performance

### Pre-commit Hooks

Validation automatique du code avant commit :

```bash
# Installation
pip install pre-commit
pre-commit install

# Hooks configurés
- black (formatting Python)
- isort (imports sorting)
- flake8 (linting)
- bandit (security scan)
- eslint (frontend linting)
```

**Configuration** : `.pre-commit-config.yaml`

### Health Checks Enrichis

Monitoring avancé avec vérifications externes :

```bash
# Health check basique
GET /health

# Health check détaillé 
GET /health/detailed
```

```json
{
  "status": "healthy",
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

**Fonctionnalités** :
- Vérification services externes (APIs tierces)
- Métriques système temps réel
- Cache intelligent (TTL 30s)
- Fallbacks robustes
- Alerting integration ready

### Monitoring Production

Métriques Prometheus exposées :

```bash
# Endpoint métriques
GET /metrics

# Métriques disponibles
metalyzr_requests_total
metalyzr_request_duration_seconds
metalyzr_cache_hits_total
metalyzr_api_errors_total
```

Intégration avec :
- **Grafana** : Dashboards visuels
- **Prometheus** : Collecte métriques
- **Alertmanager** : Notifications incidents

## Déploiement Production

### Docker Deployment

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/metalyzr
    depends_on:
      - postgres
      - redis
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: metalyzr
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
```

### Cloud Deployment Options

| Platform | Configuration | Avantages |
|----------|---------------|-----------|
| **AWS** | ECS + RDS + ElastiCache | Scaling automatique, managed services |
| **Google Cloud** | Cloud Run + Cloud SQL | Serverless, pay-per-use |
| **Azure** | App Service + Azure Database | Integration Microsoft stack |
| **DigitalOcean** | Droplets + Managed Database | Simplicité, pricing prévisible |

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          python -m pytest
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t metalyzr .
          docker push $REGISTRY/metalyzr:latest
          kubectl apply -f k8s/
```

## Tests & Qualité

### Suite de Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=src --cov-report=html

# Frontend tests  
cd frontend
npm test -- --coverage --watchAll=false

# Integration tests
python tests/integration/test_full_pipeline.py

# Performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

### Métriques Qualité

- **Code Coverage** : 85%+ requis
- **Type Coverage** : 90%+ TypeScript
- **Performance** : <200ms réponse API moyenne
- **Uptime** : 99.9% SLA target

### Quality Gates

```python
# Quality thresholds
QUALITY_GATES = {
    "classification_accuracy": 0.95,
    "api_response_time": 200,  # ms
    "error_rate": 0.01,  # 1%
    "code_coverage": 0.85,  # 85%
    "security_score": "A",
    "performance_score": 90
}
```

## Sécurité

### Mesures de Sécurité

1. **Authentification** :
   - JWT tokens avec expiration
   - API keys pour services externes
   - Rate limiting par IP

2. **Chiffrement** :
   - HTTPS obligatoire en production
   - Données sensibles chiffrées en base
   - Secrets management avec Vault

3. **Validation** :
   - Input sanitization systématique
   - SQL injection prevention
   - XSS protection

### Configuration Sécurité

```python
# Security configuration
SECURITY_CONFIG = {
    "jwt_secret": env("JWT_SECRET"),
    "token_expiry": 3600,  # 1 hour
    "rate_limits": {
        "api": "100/hour",
        "scraping": "60/hour"
    },
    "cors_origins": ["https://metalyzr.com"],
    "https_only": True
}
```

## Performance & Monitoring

### Optimisations Performance

1. **Database** :
   - Index sur colonnes fréquemment requêtées
   - Connection pooling
   - Query optimization

2. **Cache** :
   - Redis pour cache applicatif
   - CDN pour assets statiques
   - Browser caching headers

3. **API** :
   - Pagination systématique
   - Compression gzip
   - Async/await partout

### Monitoring Stack

```yaml
# Monitoring services
monitoring:
  metrics: prometheus
  logs: elasticsearch + kibana
  traces: jaeger
  uptime: pingdom
  errors: sentry
  performance: new_relic
```

### Alerting

```python
# Alert configuration
ALERTS = {
    "high_error_rate": {
        "threshold": "error_rate > 5%",
        "notification": ["slack", "email"],
        "severity": "critical"
    },
    "slow_api_response": {
        "threshold": "response_time > 500ms",
        "notification": ["slack"],
        "severity": "warning"
    }
}
```

## Contribution & Développement

### Setup Développement

```bash
# Clone avec submodules
git clone --recursive https://github.com/gbordes77/Metalyzr.git

# Install pre-commit hooks
pre-commit install

# Setup environnement développement
make dev-setup

# Run en mode développement
make dev-start
```

### Standards de Code

1. **Python** :
   - Black formatting
   - isort imports
   - flake8 linting
   - mypy type checking

2. **TypeScript** :
   - ESLint + Prettier
   - Strict type checking
   - import/export order

3. **Git** :
   - Conventional commits
   - Feature branches
   - PR reviews obligatoires

### Workflow Contribution

```mermaid
gitGraph
    commit id: "main"
    branch feature/badaro-integration
    checkout feature/badaro-integration
    commit id: "feat: add badaro engine"
    commit id: "test: integration tests"
    commit id: "docs: update readme"
    checkout main
    merge feature/badaro-integration
    commit id: "v1.2.0"
```

## Roadmap

### Version 1.0 (Q1 2025) ✅
- [x] Backend FastAPI fonctionnel
- [x] Frontend React avec dashboard
- [x] Classification Badaro intégrée
- [x] API Melee.gg client
- [x] Interface admin
- [x] Documentation complète

### Version 2.0 (Q2 2025)
- [ ] **MTGODecklistCache integration** complète
- [ ] **MTGO.com scraping** implémenté
- [ ] **WebSocket** real-time updates
- [ ] **Mobile app** iOS/Android
- [ ] **API publique** v2 avec auth
- [ ] **Multi-language** support (EN/FR/ES)

### Version 3.0 (Q3 2025)
- [ ] **Machine Learning** prediction models
- [ ] **Tournament recommender** system
- [ ] **Deck builder** integration
- [ ] **Social features** (favorites, comments)
- [ ] **Premium features** (advanced analytics)
- [ ] **Enterprise API** with SLA

### Vision Long Terme
- **AI-powered meta prediction** : Algorithmes prédictifs
- **Tournament organization tools** : Outils organisateurs
- **Player ranking system** : ELO Magic universel
- **Deck recommendation engine** : IA de construction
- **Live tournament coverage** : Streaming integration

## API Examples - Intégration Développeur

### Requêtes API Prêtes à l'Emploi

```bash
# 1. Meta snapshot Modern derniers 30 jours
curl "http://localhost:8000/api/meta-snapshot?format=Modern&days=30"

# 2. Top decks Burn avec résultats 4-0+
curl "http://localhost:8000/api/decks?archetype=Burn&min_wins=4&limit=20"

# 3. Tournois récents avec filtres
curl "http://localhost:8000/api/tournaments?format=Modern&limit=10&source=melee"

# 4. Analyse joueur spécifique
curl "http://localhost:8000/api/player-stats?player=yamakiller&format=Modern"

# 5. Classification deck en temps réel
curl -X POST "http://localhost:8000/api/classify-deck" \
  -H "Content-Type: application/json" \
  -d '{
    "mainboard": {"Lightning Bolt": 4, "Goblin Guide": 4},
    "format": "Modern"
  }'
```

### Réponses API

```json
// Meta Snapshot Response
{
  "format": "Modern",
  "period_days": 30,
  "total_decks": 2847,
  "unique_archetypes": 24,
  "archetype_breakdown": [
    {"name": "Burn", "percentage": 18.4, "decks": 524, "win_rate": 67.3},
    {"name": "UW Control", "percentage": 12.7, "decks": 362, "win_rate": 64.1},
    {"name": "Amulet Titan", "percentage": 9.8, "decks": 279, "win_rate": 71.2}
  ],
  "trends": {
    "rising": ["Burn", "Amulet Titan"],
    "falling": ["UW Control", "Jund"],
    "stable": ["Izzet Prowess", "Merfolk"]
  },
  "last_updated": "2025-01-08T17:03:42Z"
}

// Deck Classification Response  
{
  "archetype": "Burn",
  "confidence": "HIGH",
  "score": 95.2,
  "variant": "Boros Burn",
  "colors": ["R", "W"],
  "core_cards": ["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"],
  "missing_cards": ["Boros Charm", "Lightning Helix"],
  "classification_time_ms": 12
}
```

### Intégrations Possibles

```javascript
// React Component Example
const MetaDashboard = () => {
  const [metaData, setMetaData] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/meta-snapshot?format=Modern&days=30')
      .then(res => res.json())
      .then(data => setMetaData(data));
  }, []);

  return (
    <div>
      <h2>Modern Meta - {metaData?.total_decks} decks analyzed</h2>
      {metaData?.archetype_breakdown.map(arch => (
        <div key={arch.name}>
          {arch.name}: {arch.percentage}% ({arch.decks} decks)
        </div>
      ))}
    </div>
  );
};
```

```python
# Python Integration Example
import requests

def get_meta_analysis(format_name, days=30):
    response = requests.get(
        f"http://localhost:8000/api/meta-snapshot",
        params={"format": format_name, "days": days}
    )
    return response.json()

def classify_deck(mainboard, sideboard=None):
    deck_data = {"mainboard": mainboard, "sideboard": sideboard or {}}
    response = requests.post(
        "http://localhost:8000/api/classify-deck",
        json=deck_data
    )
    return response.json()

# Usage
modern_meta = get_meta_analysis("Modern", 30)
burn_classification = classify_deck({
    "Lightning Bolt": 4,
    "Goblin Guide": 4,
    "Monastery Swiftspear": 4
})
```

## Support & Communauté

### Channels de Communication

- **Issues** : [GitHub Issues](https://github.com/gbordes77/Metalyzr/issues)
- **Discussions** : [GitHub Discussions](https://github.com/gbordes77/Metalyzr/discussions)
- **Email** : metalyzr@example.com

### Documentation

- **API Reference** : [docs.metalyzr.com/api](https://docs.metalyzr.com/api)
- **Tutorials** : [docs.metalyzr.com/tutorials](https://docs.metalyzr.com/tutorials)
- **FAQ** : [docs.metalyzr.com/faq](https://docs.metalyzr.com/faq)
- **Wiki** : [github.com/gbordes77/Metalyzr/wiki](https://github.com/gbordes77/Metalyzr/wiki)

### Contributeurs

- **@gbordes77** : Creator & Lead Developer
- **@Badaro** : MTGOArchetypeParser inspiration
- **@Jiliac** : MTGODecklistCache maintenance
- **Community** : Beta testers & feedback

## Licence & Legal

### Licence MIT

```
MIT License

Copyright (c) 2025 Metalyzr Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Disclaimers

- **Magic: The Gathering** est une marque de Wizards of the Coast
- **Données tierces** : Respect des ToS de toutes les sources
- **Usage responsable** : Rate limiting et politesse web
- **Pas d'affiliation** : Projet communautaire indépendant

---

**Si Metalyzr vous aide, n'hésitez pas à donner une étoile sur GitHub !**

**Contributions welcome - Together we build the future of MTG meta analysis !**
