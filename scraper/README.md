# Metalyzr Scraper

Scraper asynchrone pour collecter les données de tournois Magic: The Gathering depuis différentes sources.

## Fonctionnalités

- **Scraping asynchrone** avec limitation de débit
- **Support multi-sources** (MTGTop8, MTGGoldfish)
- **Gestion des erreurs** robuste avec retry
- **Sauvegarde automatique** en base PostgreSQL
- **Logging détaillé** avec rotation
- **Configuration flexible** via variables d'environnement

## Sources Supportées

### MTGTop8
- Tournois par format (Standard, Modern, Legacy, etc.)
- Détails des decks avec compositions complètes
- Métadonnées des tournois (dates, lieux, organisateurs)

### MTGGoldfish (Prévu)
- Métagame analysis
- Prix des cartes
- Tendances populaires

## Installation

### Via Docker (Recommandé)
```bash
# Avec docker-compose
docker-compose up scraper

# Ou build manuel
docker build -t metalyzr-scraper .
docker run metalyzr-scraper
```

### Installation locale
```bash
cd scraper
pip install -r requirements.txt
python main.py --help
```

## Utilisation

### Commandes de base

```bash
# Scraper Standard et Modern (par défaut)
python main.py

# Scraper des formats spécifiques
python main.py --formats Standard Modern Legacy

# Limiter le nombre de tournois
python main.py --max-tournaments 5

# Afficher les statistiques uniquement
python main.py --stats-only

# Nettoyer les anciennes données
python main.py --cleanup
```

### Configuration

Variables d'environnement :

```bash
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/metalyzr

# Scraping
REQUEST_DELAY=2.0                # Délai entre requêtes (secondes)
MAX_CONCURRENT_REQUESTS=3        # Requêtes simultanées max
MAX_TOURNAMENTS_PER_RUN=10       # Tournois max par format
MAX_DECKS_PER_TOURNAMENT=100     # Decks max par tournoi

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
LOG_FILE=scraper.log            # Fichier de log
```

## Architecture

```
scraper/
├── main.py                 # Script principal
├── config.py              # Configuration
├── base_scraper.py        # Classe de base abstraite
├── mtgtop8_scraper.py     # Scraper MTGTop8
├── data_manager.py        # Gestionnaire de données
├── requirements.txt       # Dépendances
├── Dockerfile            # Image Docker
└── README.md             # Documentation
```

### Flux de données

1. **Découverte** : Recherche des tournois récents par format
2. **Extraction** : Scraping des détails de chaque tournoi
3. **Parsing** : Extraction des decks et compositions
4. **Validation** : Vérification des données
5. **Sauvegarde** : Insertion en base PostgreSQL
6. **Statistiques** : Génération des métriques

## Formats Supportés

- **Standard** : Format rotatif actuel
- **Modern** : Cartes depuis 2003
- **Legacy** : Toutes les cartes légales
- **Vintage** : Format le plus ouvert
- **Pioneer** : Cartes depuis 2012
- **Pauper** : Cartes communes uniquement

## Gestion des Erreurs

Le scraper gère automatiquement :
- **Timeouts** : Retry automatique avec backoff
- **Rate limiting** : Respect des limites des sites
- **Erreurs HTTP** : Gestion des codes d'erreur
- **Parsing errors** : Validation des données extraites
- **Database errors** : Rollback automatique

## Monitoring

### Logs
```bash
# Logs en temps réel
tail -f scraper.log

# Logs par niveau
grep "ERROR" scraper.log
```

### Métriques
```bash
# Statistiques globales
python main.py --stats-only

# Exemple de sortie :
=== STATISTIQUES METALYZR ===
Total tournois: 156
Total decks: 2,847
Formats: {'Standard': 45, 'Modern': 67, 'Legacy': 44}
Sources: {'mtgtop8': 156}
```

## Développement

### Ajouter une nouvelle source

1. Créer une classe héritant de `BaseScraper`
2. Implémenter les méthodes abstraites
3. Ajouter la configuration dans `config.py`
4. Intégrer dans `main.py`

Exemple :
```python
class NewSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__("newsite")
    
    async def scrape_tournaments(self, format_name: str, max_tournaments: int):
        # Implémentation spécifique
        pass
```

### Tests
```bash
# Tests unitaires
python -m pytest tests/

# Test d'intégration
python main.py --formats Standard --max-tournaments 1
```

## Limitations

- **Rate limiting** : Respect des limites des sites sources
- **Données manquantes** : Certains tournois peuvent être incomplets
- **Formats** : Dépend de la disponibilité sur les sites sources
- **Historique** : Limité aux données publiques disponibles

## Roadmap

- [ ] Support MTGGoldfish
- [ ] API Scryfall pour les données de cartes
- [ ] Classification automatique des archétypes
- [ ] Détection des nouvelles cartes
- [ ] Export des données (CSV, JSON)
- [ ] Interface web de monitoring
- [ ] Notifications Discord/Slack
- [ ] Métriques Prometheus

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Implémenter les changements
4. Ajouter des tests
5. Créer une Pull Request

## Licence

MIT - Voir le fichier LICENSE pour plus de détails. 