# 🚀 Guide de Démarrage Rapide - Metalyzr MVP

**Metalyzr** avec **intégrations réelles** des 3 projets GitHub MTG les plus populaires !

---

## ⚡ Installation Ultra-Rapide (5 minutes)

### Option 1 : One-Liner Magique ✨

```bash
git clone https://github.com/gbordes77/Metalyzr.git && cd Metalyzr && ./install-integrations.sh && cd backend && python3 main_simple.py
```

### Option 2 : Étapes Détaillées

```bash
# 1. Cloner le projet
git clone https://github.com/gbordes77/Metalyzr.git
cd Metalyzr

# 2. Installer les intégrations réelles
./install-integrations.sh

# 3. Lancer le backend
cd backend
python3 main_simple.py &

# 4. Lancer le frontend (nouveau terminal)
cd ../frontend
npm install && npm run build
cd build && node serve-spa.js
```

---

## 🎯 Accès Direct

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Interface utilisateur |
| **API** | http://localhost:8000 | API REST |
| **Docs** | http://localhost:8000/docs | Documentation Swagger |
| **Admin** | http://localhost:3000/admin | Panel d'administration |

---

## 🧪 Test des Intégrations

```bash
# Tester toutes les intégrations
./test-integrations.sh

# Tests individuels
curl http://localhost:8000/api/integrations/status
curl http://localhost:8000/api/integrations/supported-sites
curl http://localhost:8000/health
```

---

## 🚀 Fonctionnalités Instantanées

### 1. Obtenir des Tournois Récents avec Archétypes

```bash
curl "http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=7"
```

### 2. Scraper un Deck MTGGoldfish

```bash
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/archetype/modern-burn"}'
```

### 3. Analyse Méta Complète

```bash
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{"format": "Modern", "days": 7}'
```

---

## 📊 Dashboard Interactif

1. **Ouvrir** : http://localhost:3000
2. **Naviguer** : Tournois, Archétypes, Statistiques
3. **Utiliser** : Filtres, recherche, visualisations

---

## 🔧 Résolution de Problèmes

### Problème : "bs4 module not found"

```bash
cd backend
pip install -r requirements_integrations.txt
```

### Problème : "Port 8000 already in use"

```bash
# Tuer le processus existant
ps aux | grep python3 | grep main_simple.py | awk '{print $2}' | xargs kill -9

# Ou changer le port dans main_simple.py
```

### Problème : Frontend ne démarre pas

```bash
cd frontend
npm install
npm run build
cd build && node serve-spa.js
```

---

## 🎯 Intégrations Disponibles

### 🗃️ Jiliac Cache (MTGODecklistCache)
- **Données** : Tournois Melee, MTGO, Topdeck
- **Cache** : Local + GitHub
- **API** : `/api/integrations/tournaments/recent`

### 🕷️ MTG Scraper (fbettega)
- **Sites** : MTGGoldfish, MTGTop8, EDHRec, AetherHub, Archidekt, Moxfield, TappedOut
- **Cache** : Intelligent local
- **API** : `/api/integrations/scrape/deck`

### 🎯 Badaro Engine (MTGOArchetypeParser)
- **Classification** : Automatique par règles
- **Formats** : Modern, Standard, Legacy
- **API** : Toutes les APIs incluent la classification

---

## 📚 Documentation

- **[Guide Complet](INTEGRATIONS_REELLES.md)** : Documentation technique
- **[README](README.md)** : Vue d'ensemble
- **[API Docs](http://localhost:8000/docs)** : Swagger interface

---

## 🎮 Exemples d'Usage

### Interface Web
1. Ouvrir http://localhost:3000
2. Voir les tournois récents
3. Filtrer par format/archétype
4. Analyser les statistiques

### API REST
```bash
# Statut des intégrations
curl http://localhost:8000/api/integrations/status

# Sites supportés
curl http://localhost:8000/api/integrations/supported-sites

# Formats supportés
curl http://localhost:8000/api/integrations/supported-formats
```

---

## 🚀 Next Steps

1. **Tester** : Utiliser les APIs d'intégration
2. **Explorer** : Dashboard interactif
3. **Contribuer** : Ajouter de nouveaux sites
4. **Étendre** : Créer de nouveaux formats

---

## 🏆 Résultat

**En 5 minutes, vous avez** :
- ✅ Une plateforme MTG complète
- ✅ 3 intégrations GitHub réelles
- ✅ 7 sites de scraping
- ✅ Classification automatique d'archétypes
- ✅ Interface web + API REST

**Plus de fake data - que du concret !** 🎯 