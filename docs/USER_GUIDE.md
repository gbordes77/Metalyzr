# 📖 Guide Utilisateur - Metalyzr MVP v2.0

**Guide complet d'utilisation de la plateforme avec intégrations réelles**

---

## 🚀 Vue d'Ensemble

Metalyzr MVP v2.0 intègre maintenant **3 projets GitHub réels** pour une analyse complète du métagame MTG :

- 🗃️ **Jiliac/MTGODecklistCache** : Cache de tournois depuis GitHub
- 🕷️ **fbettega/mtg_decklist_scrapper** : Scraping de 7 sites MTG
- 🎯 **Badaro/MTGOArchetypeParser** : Classification automatique d'archétypes

---

## 🎯 Accès à la Plateforme

### URLs Principales
- **Dashboard** : http://localhost:3000
- **Panel Admin** : http://localhost:3000/admin
- **API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

### Démarrage Rapide
```bash
# Installation complète
./install-integrations.sh

# Lancement backend
cd backend && python3 main_simple.py &

# Lancement frontend
cd frontend && npm run build && cd build && node serve-spa.js
```

---

## 📊 Dashboard Principal

### 1. Vue d'Ensemble
Le dashboard présente :
- **Statistiques générales** : Nombre de tournois, archétypes, etc.
- **Tournois récents** : Avec classification automatique
- **Archétypes populaires** : Analyse du méta
- **Graphiques interactifs** : Tendances et répartitions

### 2. Fonctionnalités Interactives
- **Filtres** : Par format, date, archétype
- **Recherche** : Tournois, joueurs, archétypes
- **Export** : Données en JSON/CSV
- **Refresh** : Mise à jour temps réel

---

## 🔧 Interface d'Administration

### 1. Accès Admin
- **URL** : http://localhost:3000/admin
- **Fonctionnalités** : CRUD + Intégrations
- **Monitoring** : Statut des services

### 2. Gestion des Données
- **Créer** : Nouveaux tournois/archétypes
- **Modifier** : Données existantes
- **Supprimer** : Entrées obsolètes
- **Importer** : Données externes

---

## 🌐 APIs Disponibles

### 1. APIs CRUD Originales
```bash
# Statistiques générales
GET /api/stats

# Tournois
GET /api/tournaments
POST /api/tournaments
PUT /api/tournaments/{id}
DELETE /api/tournaments/{id}

# Archétypes
GET /api/archetypes
POST /api/archetypes
PUT /api/archetypes/{id}
DELETE /api/archetypes/{id}

# Santé
GET /health
```

### 2. Nouvelles APIs d'Intégration
```bash
# Statut des intégrations
GET /api/integrations/status

# Tournois récents avec archétypes
GET /api/integrations/tournaments/recent?format_name=Modern&days=7

# Scraping de deck
POST /api/integrations/scrape/deck
{"url": "https://www.mtggoldfish.com/deck/...", "format": "Modern"}

# Analyse méta
POST /api/integrations/meta/analysis
{"format": "Modern", "days": 7}

# Recherche par archétype
GET /api/integrations/tournaments/search?archetype=Burn

# Sites supportés
GET /api/integrations/supported-sites

# Formats supportés
GET /api/integrations/supported-formats
```

---

## 🎯 Fonctionnalités par Intégration

### 1. Cache Jiliac (Tournois GitHub)
**Utilisation** :
```bash
# Tournois récents Modern
curl "http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=7"
```

**Avantages** :
- Données historiques complètes
- Mise à jour automatique
- Cache local rapide
- Sources multiples (Melee, MTGO, Topdeck)

### 2. Scraper Multi-Sites
**Utilisation** :
```bash
# Scraper un deck MTGGoldfish
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/archetype/modern-burn"}'
```

**Sites supportés** :
- MTGGoldfish
- MTGTop8
- EDHRec
- AetherHub
- Archidekt
- Moxfield
- TappedOut

### 3. Classification Badaro
**Utilisation** :
Automatique dans tous les endpoints d'intégration.

**Fonctionnalités** :
- 12 types de conditions
- Formats Modern, Standard, Legacy
- Variantes d'archétypes
- Fallbacks intelligents

---

## 🎮 Exemples d'Usage

### 1. Analyser le Méta Modern
```bash
# 1. Obtenir les tournois récents
curl "http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=7"

# 2. Analyser les tendances
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{"format": "Modern", "days": 7}'

# 3. Rechercher un archétype spécifique
curl "http://localhost:8000/api/integrations/tournaments/search?archetype=Burn"
```

### 2. Scraper des Decks
```bash
# 1. Vérifier les sites supportés
curl http://localhost:8000/api/integrations/supported-sites

# 2. Scraper un deck MTGGoldfish
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/deck/exemple"}'

# 3. Scraper plusieurs decks
curl -X POST http://localhost:8000/api/integrations/scrape/multiple \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://site1.com/deck1", "https://site2.com/deck2"]}'
```

### 3. Utiliser l'Interface Web
1. **Ouvrir** http://localhost:3000
2. **Naviguer** dans les sections
3. **Filtrer** par format/archétype
4. **Exporter** les données

---

## 🔍 Recherche et Filtres

### 1. Filtres Disponibles
- **Format** : Modern, Standard, Legacy
- **Date** : Derniers jours/semaines
- **Archétype** : Burn, Control, Aggro, etc.
- **Source** : Jiliac, Sites scrapés, Manuel

### 2. Recherche Avancée
```bash
# Recherche par archétype
curl "http://localhost:8000/api/integrations/tournaments/search?archetype=Burn&format=Modern"

# Filtres temporels
curl "http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=30"

# Analyse méta avec filtres
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{"format": "Modern", "days": 14, "archetype": "Aggro"}'
```

---

## 📈 Données et Métriques

### 1. Types de Données
- **Tournois** : Nom, format, date, résultats
- **Decks** : Mainboard, sideboard, joueur
- **Archétypes** : Classification, confiance, variantes
- **Métriques** : Popularité, performance, tendances

### 2. Qualité des Données
- **Sources réelles** : GitHub, sites MTG
- **Classification automatique** : Moteur Badaro
- **Validation** : Checks de cohérence
- **Cache** : Performance optimisée

---

## 🔧 Personnalisation

### 1. Configuration Utilisateur
- **Formats préférés** : Modern, Standard, etc.
- **Archétypes suivis** : Notifications/alertes
- **Fréquence de mise à jour** : Paramétrable
- **Export** : Formats de données

### 2. Intégrations Tierces
- **APIs REST** : Accès programmatique
- **Webhooks** : Notifications externes
- **Export** : JSON, CSV, Excel
- **Streaming** : Données temps réel

---

## 🚀 Fonctionnalités Avancées

### 1. Analyse Méta
```bash
# Analyse complète d'un format
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "format": "Modern",
    "days": 30,
    "include_variants": true,
    "min_sample_size": 10
  }'
```

### 2. Monitoring en Temps Réel
```bash
# Statut des intégrations
curl http://localhost:8000/api/integrations/status

# Métriques système
curl http://localhost:8000/health

# Performance
curl http://localhost:8000/api/stats
```

---

## 🔍 Dépannage Utilisateur

### 1. Problèmes Courants
**Intégrations indisponibles** :
- Vérifier `curl http://localhost:8000/api/integrations/status`
- Installer dépendances : `pip install -r requirements_integrations.txt`

**Scraping échoué** :
- Vérifier l'URL
- Tester manuellement avec curl
- Consulter les sites supportés

**Données manquantes** :
- Vérifier la connectivité
- Tester les APIs de base
- Consulter les logs

### 2. Support
- **Documentation** : `INTEGRATIONS_REELLES.md`
- **API Docs** : http://localhost:8000/docs
- **Tests** : `./test-integrations.sh`

---

## 🎯 Bonnes Pratiques

### 1. Utilisation Optimale
- **Cache** : Utiliser les données cachées
- **Batch** : Grouper les requêtes
- **Filters** : Limiter les résultats
- **Monitoring** : Surveiller les performances

### 2. Sécurité
- **Rate limiting** : Respecter les limites
- **Validation** : Vérifier les données
- **Backup** : Sauvegarder les données importantes
- **Updates** : Maintenir à jour

---

## 📚 Ressources Supplémentaires

### 1. Documentation
- **[Guide Technique](../INTEGRATIONS_REELLES.md)** : Détails techniques
- **[Quick Start](../QUICK_START.md)** : Installation rapide
- **[Admin Guide](ADMIN_GUIDE.md)** : Administration

### 2. Communauté
- **GitHub** : Issues et discussions
- **API Reference** : Documentation Swagger
- **Examples** : Cas d'usage pratiques

---

## 🏆 Conclusion

**Metalyzr MVP v2.0** offre une expérience complète d'analyse du métagame MTG avec :

- ✅ **Données réelles** des 3 projets GitHub
- ✅ **Interface intuitive** web et API
- ✅ **Classification automatique** des archétypes
- ✅ **Performance optimisée** avec cache
- ✅ **Extensibilité** pour futures fonctionnalités

**Commencez dès maintenant** : `./install-integrations.sh` et explorez le dashboard !

**Plus de fake data - que du concret !** 🚀 