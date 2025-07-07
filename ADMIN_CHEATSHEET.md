# 📋 METALYZR - Aide-Mémoire Administrateur

## 🚀 Démarrage Rapide

```bash
# Démarrage complet en une commande
./final-start.sh

# Démarrage manuel
open -a Docker                           # Démarrer Docker Desktop
docker-compose up -d                     # Backend infrastructure
cd frontend/build && python3 simple-server.py  # Frontend
```

## 🔍 Vérifications de Santé

```bash
# Status général
docker-compose ps
curl -s http://localhost:8000/health
curl -I http://localhost:3000

# Logs rapides
docker-compose logs --tail=20 backend
docker-compose logs --tail=20 postgres
```

## 🛑 Arrêt des Services

```bash
# Arrêt propre
pkill -f "python3.*simple-server.py"    # Frontend
docker-compose stop                      # Backend (garde les données)

# Arrêt complet
docker-compose down                      # Supprime les conteneurs
```

## 📊 Monitoring Express

```bash
# Statistiques système
docker stats --no-stream
df -h                                    # Espace disque
lsof -i :3000,:8000,:5432,:6379         # Ports utilisés

# Métriques base de données
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "
SELECT 
  'tournaments' as table_name, COUNT(*) as count FROM tournaments
UNION ALL
SELECT 'archetypes', COUNT(*) FROM archetypes
UNION ALL
SELECT 'decks', COUNT(*) FROM decks;"
```

## 🗄️ Base de Données - Actions Rapides

```bash
# Connexion
docker-compose exec postgres psql -U metalyzr -d metalyzr

# Sauvegarde rapide
docker-compose exec postgres pg_dump -U metalyzr metalyzr > backup_$(date +%Y%m%d).sql

# Optimisation
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "VACUUM ANALYZE;"
```

## 🚨 Résolution de Problèmes

### Frontend inaccessible (Port 3000)
```bash
lsof -i :3000                           # Vérifier le port
pkill -f "python3.*simple-server.py"    # Arrêter le serveur
cd frontend/build && python3 simple-server.py  # Relancer
```

### Backend non responsive (Port 8000)
```bash
docker-compose logs backend             # Voir les erreurs
docker-compose restart backend          # Redémarrer
docker-compose exec backend python -c "print('Backend test OK')"  # Test
```

### Docker ne démarre pas
```bash
open -a Docker                          # Ouvrir Docker Desktop
docker system prune -f                  # Nettoyer si nécessaire
docker-compose down && docker-compose up -d  # Reconstruire
```

## 📈 URLs de Référence

| Service | URL | Usage |
|---------|-----|-------|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **Admin** | http://localhost:3000/admin | Administration |
| **API** | http://localhost:8000 | Backend REST |
| **Docs** | http://localhost:8000/docs | Documentation API |
| **Health** | http://localhost:8000/health | Santé du système |

## 🔧 Commandes d'Urgence

```bash
# Arrêt d'urgence complet
docker-compose kill && pkill -f "python3.*simple-server.py"

# Redémarrage d'urgence
docker-compose down && docker-compose up -d && cd frontend/build && python3 simple-server.py &

# Reset complet (⚠️ PERTE DE DONNÉES)
docker-compose down -v && docker system prune -f
```

## 📦 Export/Import Données

```bash
# Export rapide
curl -s http://localhost:8000/api/tournaments/ > tournaments.json
curl -s http://localhost:8000/api/archetypes/ > archetypes.json

# Backup DB complet
docker-compose exec postgres pg_dump -U metalyzr metalyzr | gzip > full_backup_$(date +%Y%m%d).sql.gz

# Restauration
gunzip -c backup_file.sql.gz | docker-compose exec -T postgres psql -U metalyzr metalyzr
```

## 🎯 Tâches de Maintenance

### Quotidienne (2 minutes)
```bash
docker-compose ps                        # Vérifier services
docker-compose logs backend | tail -5    # Vérifier erreurs
```

### Hebdomadaire (5 minutes)
```bash
# Sauvegarde
docker-compose exec postgres pg_dump -U metalyzr metalyzr > weekly_backup_$(date +%Y%m%d).sql

# Nettoyage
docker system prune -f
docker-compose exec postgres psql -U metalyzr -d metalyzr -c "VACUUM ANALYZE;"
```

## 📞 Support Rapide

- **Logs Frontend**: Voir terminal où tourne `simple-server.py`
- **Logs Backend**: `docker-compose logs backend`
- **Logs DB**: `docker-compose logs postgres`
- **Reset rapide**: `./final-start.sh` (redémarre tout)

## 🎨 Personnalisation Rapide

```bash
# Changer le port frontend (si 3000 occupé)
# Éditer frontend/build/simple-server.py ligne: PORT = 3001

# Ajouter plus de mémoire à PostgreSQL
# Éditer docker-compose.yml section postgres, ajouter:
# command: postgres -c shared_buffers=256MB -c max_connections=200
```

---
**💡 Conseil**: Gardez ce document ouvert dans un onglet pour un accès rapide aux commandes essentielles. 