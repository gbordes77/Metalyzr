# MVP METALYZR - Guide de démarrage

## MVP Fonctionnel (sans simulation)

Le MVP Metalyzr est fonctionnel avec de vraies données et une vraie API.

### Démarrage rapide

#### 1. Démarrer le Backend (Terminal 1)
```bash
cd backend
python3 -m venv venv_simple
source venv_simple/bin/activate
pip install -r requirements_simple.txt
python main_simple.py
```

#### 2. Démarrer le Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run build
cd build
python3 simple-server.py
```

### URLs d'accès

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

### Fonctionnalités MVP

#### Backend API
- Santé du système (`/health`)
- Statistiques globales (`/api/stats`)
- Gestion des tournois (`/api/tournaments`)
- Gestion des archétypes (`/api/archetypes`)
- Données d'exemple intégrées

#### Frontend Dashboard
- Interface avec Tailwind CSS
- Affichage des statistiques en temps réel
- Liste des tournois avec détails
- Liste des archétypes avec métriques
- Gestion d'erreurs et états de chargement
- Actualisation manuelle des données

### Test du MVP

1. **Vérifier le backend**:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
```

2. **Initialiser les données d'exemple**:
```bash
curl http://localhost:8000/api/init-sample-data
```

3. **Vérifier les données**:
```bash
curl http://localhost:8000/api/tournaments
curl http://localhost:8000/api/archetypes
```

4. **Accéder au dashboard**: http://localhost:3000

### Architecture MVP

```
MVP Metalyzr/
├── backend/
│   ├── main_simple.py      # API FastAPI simple
│   ├── requirements_simple.txt
│   └── venv_simple/        # Environnement Python
├── frontend/
│   ├── src/
│   │   ├── api/realAPI.ts  # Client API réel
│   │   ├── hooks/useRealData.ts  # Hook pour données
│   │   └── pages/RealDashboard.tsx  # Dashboard principal
│   └── build/
│       ├── simple-server.py  # Serveur React avec proxy
│       └── static/          # Assets compilés
```

### Données MVP

Le MVP contient des données d'exemple :

- **3 tournois**: Standard, Modern, Legacy
- **3 archétypes**: Mono-Red Aggro, Azorius Control, Simic Ramp
- **150 decks estimés** (50 par tournoi)

### Prochaines étapes

Maintenant que le MVP fonctionne, vous pouvez :

1. **Ajouter de vraies données** via l'API
2. **Connecter un vrai scraper** pour MTGTop8 ou MTGGoldfish
3. **Ajouter une base de données** PostgreSQL
4. **Implémenter l'authentification**
5. **Ajouter plus de fonctionnalités**

### Résolution de problèmes

#### Port déjà utilisé
```bash
# Tuer les processus existants
pkill -f "uvicorn"
pkill -f "simple-server"
```

#### Backend ne démarre pas
```bash
cd backend
pip install --upgrade -r requirements_simple.txt
```

#### Frontend erreur de build
```bash
cd frontend
rm -rf node_modules
npm install
npm run build
```

---

**MVP PRÊT !** Vous avez maintenant un système Metalyzr fonctionnel. 