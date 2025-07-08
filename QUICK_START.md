# Metalyzr - Démarrage Rapide

## Installation et Lancement (5 minutes)

### 1. Backend API (Terminal 1)

```bash
cd backend

# Créer l'environnement virtuel (première fois seulement)
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements_simple.txt

# Démarrer le backend
./start-backend.sh
```

### 2. Frontend React (Terminal 2)

```bash
cd frontend

# Démarrer le frontend
./start-frontend.sh
```

### 3. Accéder à l'application

- **Application**: http://localhost:3000
- **Admin**: http://localhost:3000/admin
- **API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

### 4. Vérifier les services

```bash
# Health check basique
curl http://localhost:8000/health

# Health check détaillé avec services externes
curl http://localhost:8000/health/detailed

# Métriques Prometheus
curl http://localhost:8000/metrics
```

### 5. Initialiser les données (optionnel)

```bash
# Charger données d'exemple
curl http://localhost:8000/api/init-sample-data

# Vérifier le cache MTGODecklistCache
curl http://localhost:8000/api/cache/status
```

## Script tout-en-un

Pour démarrer les deux services en même temps :

```bash
./start-metalyzr.sh
```

## Vérification rapide

```bash
# Backend
curl http://localhost:8000/health

# Frontend  
curl http://localhost:3000
```

## Résolution de problèmes

### "Address already in use"
```bash
# Tuer les processus sur les ports
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

### "venv_new not found"
```bash
cd backend
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements_simple.txt
```

### "serve-spa.js not found"
Le fichier existe déjà dans `frontend/build/serve-spa.js`. Si problème :
```bash
cd frontend/build
node serve-spa.js
```

## Architecture

```
Metalyzr/
├── backend/          # FastAPI (port 8000)
│   ├── main_simple.py
│   ├── venv_new/
│   └── start-backend.sh
├── frontend/         # React (port 3000)  
│   ├── build/
│   │   └── serve-spa.js
│   └── start-frontend.sh
└── start-metalyzr.sh # Script global
```

---

**Le projet fonctionne maintenant !** 

Les services backend et frontend sont opérationnels avec des données d'exemple.

## Développement

### Configuration pre-commit hooks

```bash
# Installation (dans le dossier backend)
cd backend
pip install pre-commit
pre-commit install

# Test manual des hooks
pre-commit run --all-files
```

### Tests automatisés

```bash
# Tests backend
cd backend
python -m pytest -v

# Tests frontend  
cd frontend
npm test

# Tests d'intégration
python test_integration_complete.py
```

### Pipeline CI/CD

Les tests s'exécutent automatiquement sur :
- Chaque push vers `main`
- Chaque pull request
- Tests multi-versions Python (3.8-3.11)
- Validation Docker builds

### Endpoints de monitoring

```bash
# Health checks
curl http://localhost:8000/health          # Basique
curl http://localhost:8000/health/detailed # Complet avec services externes

# Métriques Prometheus  
curl http://localhost:8000/metrics

# Status du cache
curl http://localhost:8000/api/cache/status
```

## Production

### Variables d'environnement

```bash
# .env pour production
DATABASE_URL=postgresql://user:pass@localhost/metalyzr
REDIS_URL=redis://localhost:6379
MELEE_API_TOKEN=your_token_here
LOG_LEVEL=INFO
```

### Docker deployment

```bash
# Build et démarrage
docker-compose up -d

# Health check
curl http://localhost:8000/health/detailed
``` 