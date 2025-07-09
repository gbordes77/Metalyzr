# 🎯 Metalyzr MVP - Version Honnête

> **MVP basique mais fonctionnel - Plus de fake data !**

## 🧹 Nettoyage effectué

- ❌ **Supprimé** : Cache fake, APIs externes fake, monitoring fake
- ❌ **Supprimé** : MTGODecklistCache, Health checks complexes
- ❌ **Supprimé** : Données d'exemple, statistiques simulées
- ✅ **Gardé** : CRUD réel, stockage JSON, API REST complète

## 🔧 Fonctionnalités réelles

### Backend (FastAPI)
- API REST complète avec documentation Swagger
- CRUD tournois et archétypes
- Stockage JSON local fiable
- Statistiques dynamiques calculées
- Validation des données avec Pydantic

### Frontend (React)
- Interface web moderne
- Formulaires de saisie manuelle
- Visualisation des données
- Connexion API temps réel

## 🚀 Démarrage rapide

```bash
# Démarrer le MVP
./start-mvp-honest.sh

# Arrêter le MVP
./stop-mvp-honest.sh
```

## 📊 Endpoints disponibles

- **Backend** : http://localhost:8000
- **API docs** : http://localhost:8000/docs
- **Frontend** : http://localhost:3000
- **Health** : http://localhost:8000/health

## 💾 Stockage des données

Les données sont stockées localement dans `backend/data/` :
- `tournaments.json` : Tournois créés
- `archetypes.json` : Archétypes créés

## 🔧 API REST

### Tournois
- `GET /api/tournaments` - Liste des tournois
- `POST /api/tournaments` - Créer un tournoi
- `GET /api/tournaments/{id}` - Détails d'un tournoi
- `PUT /api/tournaments/{id}` - Modifier un tournoi
- `DELETE /api/tournaments/{id}` - Supprimer un tournoi

### Archétypes
- `GET /api/archetypes` - Liste des archétypes
- `POST /api/archetypes` - Créer un archétype
- `GET /api/archetypes/{id}` - Détails d'un archétype
- `PUT /api/archetypes/{id}` - Modifier un archétype
- `DELETE /api/archetypes/{id}` - Supprimer un archétype

### Stats
- `GET /api/stats` - Statistiques globales

## 📝 Exemple d'utilisation

```bash
# Créer un tournoi
curl -X POST http://localhost:8000/api/tournaments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FNM Local",
    "format": "Standard",
    "date": "2025-07-10",
    "participants": 16,
    "organizer": "Magasin Local",
    "description": "Friday Night Magic Standard"
  }'

# Créer un archétype
curl -X POST http://localhost:8000/api/archetypes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Midrange",
    "description": "Deck équilibré aggro-contrôle",
    "format": "Standard",
    "colors": "White Blue"
  }'

# Voir les stats
curl http://localhost:8000/api/stats
```

## 💡 Philosophie du MVP

Ce MVP est **honnête** et **fonctionnel** :
- Pas de fake data qui trompe l'utilisateur
- Saisie manuelle uniquement
- Fonctionnalités simples mais qui marchent vraiment
- Base solide pour extensions futures

## 🛠️ Prochaines étapes possibles

1. **Interface améliorée** : Meilleurs formulaires, validation
2. **Import CSV** : Importer des données de tournois
3. **Statistiques avancées** : Graphiques, tendances
4. **Authentification** : Gestion d'utilisateurs
5. **API externes réelles** : Intégration melee.gg (vraie)

---

**✅ Système testé et fonctionnel - Pas de fake !** 