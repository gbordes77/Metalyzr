# 🚀 Metalyzr - Démarrage Rapide

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

- 🌐 **Application**: http://localhost:3000
- 👨‍💼 **Admin**: http://localhost:3000/admin
- 🔧 **API**: http://localhost:8000
- 📚 **Documentation API**: http://localhost:8000/docs

### 4. Initialiser les données (optionnel)

```bash
curl http://localhost:8000/api/init-sample-data
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

### ❌ "Address already in use"
```bash
# Tuer les processus sur les ports
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

### ❌ "venv_new not found"
```bash
cd backend
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r requirements_simple.txt
```

### ❌ "serve-spa.js not found"
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

✅ **Le projet fonctionne maintenant !** 

Les services backend et frontend sont opérationnels avec des données d'exemple. 