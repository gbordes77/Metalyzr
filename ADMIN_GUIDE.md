# 👨‍💼 METALYZR - Guide Administrateur

## 🎯 Vue d'Ensemble

Ce guide détaille l'administration complète de la plateforme Metalyzr, incluant la gestion des services, la maintenance, le monitoring et les opérations avancées.

## 📊 Architecture du Système

### Services Principaux
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   React SPA     │───▶│   FastAPI       │───▶│   PostgreSQL    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cache         │
                       │   Redis         │
                       │   Port: 6379    │
                       └─────────────────┘
```

### Infrastructure
- **Environnement**: Docker Compose
- **Base de données**: PostgreSQL 15
- **Cache**: Redis 7
- **Serveur web**: Python custom server avec CORS
- **Reverse Proxy**: Intégré au serveur frontend

## 🚀 Démarrage et Arrêt des Services

### Démarrage Complet (Recommandé)
```bash
# 1. Démarrer Docker Desktop (macOS)
open -a Docker

# 2. Attendre que Docker soit prêt (icône verte)
# 3. Démarrer l'infrastructure backend
docker-compose up -d

# 4. Démarrer le frontend
cd frontend/build
python3 simple-server.py
```

### Démarrage Automatique
```bash
# Utiliser le script de démarrage automatique
./final-start.sh
```

### Démarrage Sélectif
```bash
# Backend uniquement
docker-compose up -d backend postgres redis

# Frontend uniquement (si backend déjà lancé)
cd frontend/build && python3 simple-server.py

# Base de données uniquement
docker-compose up -d postgres redis
```

### Arrêt des Services
```bash
# Arrêt frontend
pkill -f "python3.*simple-server.py"

# Arrêt backend (garder les données)
docker-compose stop

# Arrêt complet avec suppression des conteneurs
docker-compose down

# Arrêt avec suppression des volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v
```

## 🔍 Monitoring et Surveillance

### URLs de Monitoring
| Service | URL | Description |
|---------|-----|-------------|
| **Health Check** | http://localhost:8000/health | Santé de l'API |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger |
| **Admin Dashboard** | http://localhost:3000/admin | Interface d'administration |
| **Frontend** | http://localhost:3000 | Application principale |

### Commandes de Vérification
```bash
# Statut des conteneurs
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs backend
docker-compose logs postgres

# Utilisation des ressources
docker stats

# Connexions réseau
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

### Tests de Santé
```bash
# Test API Backend
curl -s http://localhost:8000/health | jq

# Test Frontend
curl -I http://localhost:3000

# Test base de données (depuis le conteneur)
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "SELECT version();"

# Test Redis
docker-compose exec redis redis-cli ping
```

## 📊 Interface d'Administration

### Accès Admin Dashboard
- **URL**: http://localhost:3000/admin
- **Fonctionnalités**:
  - Monitoring système en temps réel
  - Gestion des scraping
  - Export de données
  - Statistiques détaillées

### Fonctionnalités Administratives

#### 1. Monitoring Système
```bash
# Statistiques système
curl -s http://localhost:8000/api/tournaments/ | jq length  # Nombre de tournois
curl -s http://localhost:8000/api/archetypes/ | jq length  # Nombre d'archétypes
```

#### 2. Gestion des Données
```bash
# Export des données
curl -s http://localhost:8000/api/tournaments/ > tournaments_backup.json
curl -s http://localhost:8000/api/archetypes/ > archetypes_backup.json

# Vérification de l'intégrité
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "
  SELECT 
    (SELECT COUNT(*) FROM tournaments) as tournaments,
    (SELECT COUNT(*) FROM archetypes) as archetypes,
    (SELECT COUNT(*) FROM decks) as decks;
"
```

## 🗄️ Gestion de la Base de Données

### Connexion à PostgreSQL
```bash
# Via Docker
docker-compose exec postgres psql -U metalyzr -d metalyzr

# Connexion directe
psql -h localhost -p 5432 -U metalyzr -d metalyzr
```

### Requêtes Administratives Utiles
```sql
-- Statistiques générales
SELECT 
  'tournaments' as table_name, COUNT(*) as count FROM tournaments
UNION ALL
SELECT 'archetypes', COUNT(*) FROM archetypes
UNION ALL
SELECT 'decks', COUNT(*) FROM decks
UNION ALL
SELECT 'cards', COUNT(*) FROM cards;

-- Tournois récents
SELECT name, date, format, player_count 
FROM tournaments 
ORDER BY date DESC 
LIMIT 10;

-- Archétypes populaires
SELECT a.name, COUNT(d.id) as deck_count
FROM archetypes a
LEFT JOIN decks d ON a.id = d.archetype_id
GROUP BY a.id, a.name
ORDER BY deck_count DESC;

-- Vérification de l'intégrité référentielle
SELECT 'Decks without archetype' as issue, COUNT(*) as count
FROM decks WHERE archetype_id IS NULL
UNION ALL
SELECT 'Decks without tournament', COUNT(*)
FROM decks d
LEFT JOIN tournament_deck_association tda ON d.id = tda.deck_id
WHERE tda.deck_id IS NULL;
```

### Sauvegardes
```bash
# Sauvegarde complète
docker-compose exec postgres pg_dump -U metalyzr metalyzr > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde avec compression
docker-compose exec postgres pg_dump -U metalyzr metalyzr | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restauration
docker-compose exec -T postgres psql -U metalyzr metalyzr < backup_file.sql
```

## 🔧 Maintenance et Dépannage

### Problèmes Courants

#### 1. Frontend Inaccessible (ERR_CONNECTION_REFUSED)
```bash
# Diagnostic
lsof -i :3000

# Solution
cd frontend/build
python3 simple-server.py
```

#### 2. API Backend Non Responsive
```bash
# Vérifier les logs
docker-compose logs backend

# Redémarrer le service
docker-compose restart backend

# Vérifier la connectivité DB
docker-compose exec backend python -c "
from app.database import engine
print('DB Connection:', engine.url)
"
```

#### 3. Base de Données Corrompue
```bash
# Vérifier l'état
docker-compose exec postgres pg_isready -U metalyzr

# Réparer si nécessaire
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "REINDEX DATABASE metalyzr;"

# En dernier recours : reconstruction
docker-compose down -v
docker-compose up -d postgres
# Restaurer depuis backup
```

#### 4. Problèmes de Performance
```bash
# Analyser les ressources
docker stats

# Logs détaillés
docker-compose logs --tail=100 backend

# Optimiser PostgreSQL
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "
ANALYZE;
VACUUM ANALYZE;
"
```

### Nettoyage et Optimisation
```bash
# Nettoyer les images Docker inutilisées
docker system prune -f

# Nettoyer les volumes orphelins
docker volume prune -f

# Logs de rotation
docker-compose logs --tail=1000 > logs_archive_$(date +%Y%m%d).log

# Optimisation base de données
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "
VACUUM ANALYZE;
REINDEX DATABASE metalyzr;
"
```

## 📈 Scaling et Performance

### Monitoring des Performances
```bash
# Métriques système
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Métriques base de données
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;
"
```

### Optimisations Recommandées
```sql
-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_tournaments_date ON tournaments(date);
CREATE INDEX IF NOT EXISTS idx_tournaments_format ON tournaments(format);
CREATE INDEX IF NOT EXISTS idx_decks_archetype ON decks(archetype_id);
CREATE INDEX IF NOT EXISTS idx_tournament_deck_tournament ON tournament_deck_association(tournament_id);
```

## 🔐 Sécurité et Accès

### Configurations de Sécurité
```bash
# Variables d'environnement sensibles
# À définir dans un fichier .env (non versionné)
cat > .env << EOF
DATABASE_URL=postgresql://metalyzr:secure_password@localhost:5432/metalyzr
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key_here
API_RATE_LIMIT=100
EOF
```

### Accès aux Logs
```bash
# Logs d'accès frontend
tail -f /var/log/metalyzr/access.log

# Logs d'erreur backend
docker-compose logs backend | grep ERROR

# Logs de sécurité
docker-compose logs | grep -i "unauthorized\|failed\|error"
```

## 📋 Tâches de Maintenance Régulières

### Quotidiennes
- [ ] Vérifier le statut des services : `docker-compose ps`
- [ ] Contrôler l'espace disque : `df -h`
- [ ] Vérifier les logs d'erreur : `docker-compose logs | grep ERROR`

### Hebdomadaires
- [ ] Sauvegarde de la base de données
- [ ] Nettoyage des logs anciens
- [ ] Mise à jour des statistiques : `VACUUM ANALYZE`
- [ ] Vérification des performances : `docker stats`

### Mensuelles
- [ ] Sauvegarde complète du système
- [ ] Mise à jour des images Docker
- [ ] Analyse des métriques de performance
- [ ] Test de restauration des sauvegardes

## 🚨 Procédures d'Urgence

### Arrêt d'Urgence
```bash
# Arrêt immédiat de tous les services
docker-compose kill
pkill -f "python3.*simple-server.py"
```

### Restauration Rapide
```bash
# 1. Arrêter tous les services
docker-compose down

# 2. Restaurer depuis backup
docker-compose up -d postgres
docker-compose exec -T postgres psql -U metalyzr metalyzr < latest_backup.sql

# 3. Redémarrer tous les services
docker-compose up -d
cd frontend/build && python3 simple-server.py &
```

### Contacts d'Urgence
- **Développeur Principal**: guillaume.bordes@example.com
- **Documentation**: https://github.com/gbordes77/Metalyzr
- **Issues**: https://github.com/gbordes77/Metalyzr/issues

## 📚 Ressources Supplémentaires

### Documentation Technique
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Architecture détaillée
- [QUICK_START.md](./QUICK_START.md) - Guide de démarrage rapide
- [API Documentation](http://localhost:8000/docs) - Swagger API

### Outils Utiles
- **Swagger UI**: http://localhost:8000/docs
- **PostgreSQL Admin**: pgAdmin ou DBeaver
- **Redis CLI**: `docker-compose exec redis redis-cli`
- **Logs Viewer**: `docker-compose logs -f`

---

**Version**: 1.0.0 | **Dernière mise à jour**: 2025-07-07 | **Maintenu par**: Guillaume Bordes 