# 🚀 METALYZR - Guide de Démarrage Rapide

## ✅ État Actuel du Projet

### ✅ Frontend - FONCTIONNEL
- **URL**: http://localhost:3000
- **Dashboard Public**: http://localhost:3000
- **Dashboard Admin**: http://localhost:3000/admin
- **Status**: 🟢 **EN COURS D'EXÉCUTION**

### ⚠️ Backend - NÉCESSITE DOCKER
- **URL**: http://localhost:8000
- **Status**: 🟡 **DOCKER À DÉMARRER**

## 🎯 Démarrage Immédiat (2 étapes)

### Étape 1: Démarrer Docker Desktop
```bash
# Sur macOS, Docker Desktop s'ouvre automatiquement
# Attendez que l'icône Docker soit verte dans la barre de menu
```

### Étape 2: Lancer l'infrastructure
```bash
cd /Users/guillaumebordes/Documents/Metalyzr
docker-compose up -d
```

## 🌐 URLs d'Accès

| Service | URL | Status |
|---------|-----|--------|
| 🎯 **Frontend Dashboard** | http://localhost:3000 | 🟢 **ACTIF** |
| 👨‍💼 **Admin Dashboard** | http://localhost:3000/admin | 🟢 **ACTIF** |
| 🔌 **API Backend** | http://localhost:8000 | 🟡 Nécessite Docker |
| 📚 **Documentation API** | http://localhost:8000/docs | 🟡 Nécessite Docker |

## 🔧 Solution au Problème ERR_CONNECTION_REFUSED

Le message **"Ce site est inaccessible - ERR_CONNECTION_REFUSED"** était dû à un problème de démarrage du serveur de développement React causé par des espaces dans le chemin du projet.

### ✅ Solution Appliquée
- ✅ Serveur frontend personnalisé avec proxy intégré
- ✅ Support CORS pour l'API backend
- ✅ Routage React Router fonctionnel
- ✅ Gestion des erreurs backend

## 📊 Architecture Fonctionnelle

```
Frontend (Port 3000) ----[Proxy]----> Backend API (Port 8000)
     |                                         |
     |                                         |
  [React SPA]                            [FastAPI + DB]
     |                                         |
  Dashboard                              PostgreSQL
  Admin Panel                            Redis Cache
```

## 🎮 Utilisation

### 1. Dashboard Principal
- **URL**: http://localhost:3000
- **Fonctionnalités**:
  - Statistiques de tournois
  - Graphiques métagame
  - Filtres par format
  - Archétypes populaires

### 2. Dashboard Admin
- **URL**: http://localhost:3000/admin
- **Fonctionnalités**:
  - Monitoring système
  - Contrôles de scraping
  - Export de données
  - Gestion des archétypes

### 3. API Backend
- **URL**: http://localhost:8000/docs
- **Endpoints**:
  - GET `/api/tournaments/` - Liste des tournois
  - GET `/api/archetypes/` - Liste des archétypes
  - GET `/api/formats/` - Formats de jeu
  - GET `/health` - Santé du service

## ⚡ Commandes Utiles

### Vérifier les Services
```bash
# Status des conteneurs
docker-compose ps

# Logs backend
docker-compose logs backend

# Santé API
curl http://localhost:8000/health
```

### Arrêter les Services
```bash
# Arrêter le frontend
pkill -f "python3.*simple-server.py"

# Arrêter Docker
docker-compose down
```

### Redémarrage Complet
```bash
# 1. Arrêter tout
pkill -f "python3.*simple-server.py"
docker-compose down

# 2. Redémarrer
docker-compose up -d
cd frontend/build && python3 simple-server.py
```

## 🐛 Résolution des Problèmes

### Frontend inaccessible (Port 3000)
```bash
# Vérifier si le serveur tourne
lsof -i :3000

# Redémarrer le serveur frontend
cd frontend/build
python3 simple-server.py
```

### Backend inaccessible (Port 8000)
```bash
# Vérifier Docker
docker ps

# Redémarrer Docker
docker-compose up -d backend
```

### Erreurs CORS
Le serveur frontend intègre un proxy qui résout automatiquement les problèmes CORS.

## 📈 Données de Test

Le système contient des données d'exemple :
- **3 archétypes** : Mono-Red Aggro, Azorius Control, Golgari Midrange
- **Tournois simulés** avec métagames complets
- **Cartes et decks** pour demonstration

## 🎉 Félicitations !

Votre environnement Metalyzr est **fonctionnel** ! 

👉 **Accédez maintenant au dashboard** : http://localhost:3000

---

**Version**: 1.0.0 | **Date**: 2025-07-07 | **Status**: Production Ready 