# 👨‍💼 Guide d'Administration - Metalyzr MVP

**Administration complète de la plateforme avec intégrations réelles**

---

## 🚀 Vue d'Ensemble

Metalyzr MVP intègre maintenant **3 projets GitHub réels** :
- 🗃️ **Jiliac/MTGODecklistCache** : Cache de tournois
- 🕷️ **fbettega/mtg_decklist_scrapper** : Scraping multi-sites
- 🎯 **Badaro/MTGOArchetypeParser** : Classification d'archétypes

---

## 🛠️ Installation Admin

### 1. Installation Complète

```bash
# Installation avec intégrations
./install-integrations.sh

# Vérification
./test-integrations.sh
```

### 2. Services à Surveiller

| Service | Port | Statut | Health Check |
|---------|------|--------|--------------|
| **Backend API** | 8000 | ✅ | `curl http://localhost:8000/health` |
| **Frontend** | 3000 | ✅ | `curl http://localhost:3000` |
| **Intégrations** | - | ✅ | `curl http://localhost:8000/api/integrations/status` |

---

## 📊 Monitoring et Santé

### 1. Health Checks

```bash
# Santé générale
curl http://localhost:8000/health

# Statut des intégrations
curl http://localhost:8000/api/integrations/status

# Sites de scraping disponibles
curl http://localhost:8000/api/integrations/supported-sites
```

### 2. Métriques Importantes

```bash
# Formats supportés
curl http://localhost:8000/api/integrations/supported-formats

# Statistiques générales
curl http://localhost:8000/api/stats

# Données de base
curl http://localhost:8000/api/tournaments
curl http://localhost:8000/api/archetypes
```

---

## 🔧 Configuration des Intégrations

### 1. Cache Jiliac

**Paramètres** :
- **Source** : GitHub MTGODecklistCache
- **Cache local** : `backend/cache/integrations/jiliac/`
- **Rafraîchissement** : Manuel via API

```bash
# Tester le cache Jiliac
curl "http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=7"
```

### 2. Scraper MTG

**Sites supportés** :
- MTGGoldfish
- MTGTop8
- EDHRec
- AetherHub
- Archidekt
- Moxfield
- TappedOut

```bash
# Tester le scraper
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/archetype/modern-burn"}'
```

### 3. Moteur Badaro

**Formats configurés** :
- Modern
- Standard  
- Legacy (extensible)

```bash
# Test de classification
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{"format": "Modern", "days": 7}'
```

---

## 🔍 Gestion des Données

### 1. Sources de Données

| Source | Type | Rafraîchissement | Cache |
|--------|------|------------------|-------|
| **Jiliac GitHub** | Automatique | À la demande | Local |
| **Sites MTG** | Scraping | À la demande | Local |
| **Classification** | Engine | Temps réel | Mémoire |
| **CRUD Manuel** | Interface | Temps réel | JSON |

### 2. Gestion du Cache

```bash
# Localisation du cache
ls -la backend/cache/integrations/
├── jiliac/           # Cache tournois GitHub
├── scraper/          # Cache pages scrapées
└── archetype_formats/  # Règles de classification
```

### 3. Maintenance

```bash
# Nettoyer le cache (si nécessaire)
rm -rf backend/cache/integrations/jiliac/*
rm -rf backend/cache/integrations/scraper/*

# Réinstaller les intégrations
./install-integrations.sh
```

---

## 🎯 Interface d'Administration

### 1. Accès Admin

- **URL** : http://localhost:3000/admin
- **Authentification** : Aucune (MVP)
- **Fonctionnalités** : CRUD + Intégrations

### 2. Opérations Disponibles

**CRUD Basique** :
- ✅ Créer tournois
- ✅ Modifier archétypes
- ✅ Supprimer entrées
- ✅ Visualiser statistiques

**Intégrations** :
- ✅ Statut des services
- ✅ Test des APIs
- ✅ Monitoring temps réel

---

## 🛡️ Sécurité et Limites

### 1. Rate Limiting

**Intégrations** :
- Scraping : Headers respectueux
- GitHub : Limite naturelle
- Classification : Pas de limite

### 2. Gestion d'Erreurs

```bash
# Logs d'erreurs
tail -f backend/logs/error.log

# Statut des services
curl http://localhost:8000/api/integrations/status
```

### 3. Fallbacks

- **Intégrations indisponibles** → Mode MVP basique
- **Scraping échoué** → Données cached
- **Classification échouée** → Fallback couleur

---

## 🔄 Workflows Administratifs

### 1. Démarrage Quotidien

```bash
# 1. Vérifier les services
curl http://localhost:8000/health

# 2. Tester les intégrations
curl http://localhost:8000/api/integrations/status

# 3. Vérifier le frontend
curl http://localhost:3000
```

### 2. Maintenance Hebdomadaire

```bash
# 1. Nettoyer les logs
rm -f backend/logs/*.log

# 2. Tester toutes les intégrations
./test-integrations.sh

# 3. Vérifier la performance
curl http://localhost:8000/api/stats
```

### 3. Résolution de Problèmes

**Problème : Intégrations indisponibles**
```bash
# Réinstaller les dépendances
cd backend
pip install -r requirements_integrations.txt

# Redémarrer le backend
python3 main_simple.py
```

**Problème : Scraping échoué**
```bash
# Vérifier les sites supportés
curl http://localhost:8000/api/integrations/supported-sites

# Tester manuellement
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/deck/test"}'
```

---

## 📈 Performance et Optimisation

### 1. Métriques Clés

- **Temps de réponse API** : <200ms
- **Cache hit rate** : >80%
- **Disponibilité** : >99%

### 2. Optimisations

```bash
# Pré-charger le cache
curl "http://localhost:8000/api/integrations/tournaments/recent"

# Tester la performance
time curl http://localhost:8000/api/stats
```

---

## 🚀 Extensions Futures

### 1. Ajout de Nouveaux Sites

```python
# Dans backend/integrations/mtg_scraper.py
def _scrape_nouveau_site(self, url: str) -> Optional[Dict]:
    # Votre logique de scraping
    pass

# Enregistrer dans supported_sites
self.supported_sites['nouveau-site.com'] = self._scrape_nouveau_site
```

### 2. Nouveaux Formats

```bash
# Créer la structure
mkdir -p backend/cache/integrations/archetype_formats/NOUVEAU_FORMAT/{archetypes,fallbacks}

# Ajouter les règles JSON
# Voir INTEGRATIONS_REELLES.md pour les détails
```

---

## 📞 Support et Debugging

### 1. Logs Utiles

```bash
# Logs du backend
tail -f backend/logs/app.log

# Logs système
dmesg | tail

# Processus actifs
ps aux | grep python3
```

### 2. Tests de Diagnostic

```bash
# Test complet
./test-integrations.sh

# Test spécifique
curl http://localhost:8000/api/integrations/status -v
```

### 3. Ressources

- **Documentation** : `INTEGRATIONS_REELLES.md`
- **API Docs** : http://localhost:8000/docs
- **Quick Start** : `QUICK_START.md`

---

## 🏆 Checklist Admin

### Quotidien
- [ ] Vérifier health checks
- [ ] Tester les intégrations
- [ ] Surveiller les logs

### Hebdomadaire
- [ ] Nettoyer le cache
- [ ] Tester toutes les APIs
- [ ] Vérifier la performance

### Mensuel
- [ ] Mettre à jour les dépendances
- [ ] Réviser la documentation
- [ ] Analyser les métriques

---

**✅ Metalyzr MVP est maintenant une plateforme complète avec administration simplifiée !**

**Pour toute question : voir la documentation complète ou tester les APIs directement.** 