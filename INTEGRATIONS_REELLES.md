# 🚀 Intégrations Réelles - Metalyzr MVP

## 📋 Vue d'ensemble

Metalyzr MVP intègre désormais **3 projets GitHub réels** pour automatiser l'analyse du méta Magic The Gathering :

### 1. **Jiliac/MTGODecklistCache** 🗃️
- **Fonction** : Cache de tournois JSON depuis GitHub
- **Sources** : Melee, MTGO, Topdeck
- **Données** : Tournois, decklists, joueurs
- **Statut** : ✅ Intégration active

### 2. **fbettega/mtg_decklist_scrapper** 🕷️
- **Fonction** : Scraping de sites MTG
- **Sites supportés** : MTGGoldfish, MTGTop8, EDHRec, AetherHub, Archidekt, Moxfield, TappedOut
- **Données** : Decklists, cartes, sideboard
- **Statut** : ✅ Intégration active

### 3. **Badaro/MTGOArchetypeParser** 🎯
- **Fonction** : Classification d'archétypes
- **Langages** : Porté de C# vers Python
- **Données** : Archétypes, variantes, conditions
- **Statut** : ✅ Intégration active

---

## 🔧 Installation

```bash
# Installer les dépendances
./install-integrations.sh

# Lancer le serveur
cd backend
python3 main_simple.py
```

---

## 🌐 API Endpoints

### Statut des intégrations
```
GET /api/integrations/status
```

### Tournois récents avec archétypes
```
GET /api/integrations/tournaments/recent?format_name=Modern&days=7
```

### Scraping de deck
```
POST /api/integrations/scrape/deck
Body: {"url": "https://mtggoldfish.com/deck/...", "format": "Modern"}
```

### Scraping multiple
```
POST /api/integrations/scrape/multiple
Body: ["url1", "url2", "url3"]
```

### Analyse méta
```
POST /api/integrations/meta/analysis
Body: {"format": "Modern", "days": 7}
```

### Recherche par archétype
```
GET /api/integrations/tournaments/search?archetype=Burn&format_name=Modern
```

### Sites supportés
```
GET /api/integrations/supported-sites
```

### Formats supportés
```
GET /api/integrations/supported-formats
```

---

## 📊 Exemples d'utilisation

### 1. Obtenir des tournois récents classifiés
```bash
curl http://localhost:8000/api/integrations/tournaments/recent?format_name=Modern&days=7
```

**Réponse** :
```json
{
  "tournaments": [
    {
      "tournament": {
        "name": "Modern Tournament",
        "date": "2024-01-15",
        "format": "Modern",
        "source": "mtgo"
      },
      "decks": [
        {
          "player": "Player1",
          "mainboard": [...],
          "sideboard": [...],
          "archetype_classification": {
            "archetype": "R Burn",
            "base_archetype": "Burn",
            "colors": "R",
            "confidence": 1.0
          }
        }
      ]
    }
  ]
}
```

### 2. Scraper un deck depuis MTGGoldfish
```bash
curl -X POST http://localhost:8000/api/integrations/scrape/deck \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.mtggoldfish.com/archetype/modern-burn", "format": "Modern"}'
```

**Réponse** :
```json
{
  "name": "Modern Burn",
  "source": "mtggoldfish.com",
  "url": "https://www.mtggoldfish.com/archetype/modern-burn",
  "mainboard": [
    {"name": "Lightning Bolt", "count": 4},
    {"name": "Monastery Swiftspear", "count": 4}
  ],
  "sideboard": [...],
  "archetype_classification": {
    "archetype": "R Burn",
    "base_archetype": "Burn",
    "colors": "R",
    "confidence": 1.0
  }
}
```

### 3. Analyse complète du méta
```bash
curl -X POST http://localhost:8000/api/integrations/meta/analysis \
  -H "Content-Type: application/json" \
  -d '{"format": "Modern", "days": 7}'
```

**Réponse** :
```json
{
  "format": "Modern",
  "total_decks": 1250,
  "total_tournaments": 15,
  "archetypes": {
    "R Burn": {
      "count": 125,
      "percentage": 10.0,
      "win_rate": 0.52
    },
    "UW Control": {
      "count": 87,
      "percentage": 6.96,
      "win_rate": 0.48
    }
  },
  "top_archetypes": [...]
}
```

---

## 🔧 Architecture technique

### Structure des dossiers
```
backend/
├── integrations/
│   ├── __init__.py
│   ├── jiliac_cache.py          # Cache Jiliac
│   ├── mtg_scraper.py           # Scraper MTG
│   ├── badaro_archetype_engine.py # Engine Badaro
│   └── integration_service.py    # Service principal
├── cache/
│   └── integrations/
│       ├── jiliac/              # Cache Jiliac
│       ├── scraper/             # Cache scraper
│       └── archetype_formats/   # Données archétypes
└── main_simple.py               # API principale
```

### Flux de données
```
1. Jiliac Cache → Tournois récents
2. Badaro Engine → Classification des decks
3. MTG Scraper → Decklists depuis sites
4. Integration Service → Combine tout
```

---

## ⚙️ Configuration

### Moteur d'archétypes
Les archétypes sont définis dans `cache/integrations/archetype_formats/FORMAT/`:

```json
{
  "name": "Burn",
  "include_color_in_name": true,
  "conditions": [
    {
      "type": "InMainboard",
      "cards": ["Lightning Bolt"]
    },
    {
      "type": "OneOrMoreInMainboard", 
      "cards": ["Monastery Swiftspear", "Goblin Guide"]
    }
  ]
}
```

### Types de conditions supportés
- `InMainboard` : Toutes les cartes en main
- `InSideboard` : Toutes les cartes en side
- `OneOrMoreInMainboard` : Au moins une carte en main
- `TwoOrMoreInMainboard` : Au moins deux cartes en main
- `DoesNotContain` : Aucune des cartes présentes

---

## 🧪 Tests

```bash
# Installer et tester
./test-integrations.sh
```

**Test des fonctionnalités** :
- ✅ Statut des intégrations
- ✅ Sites de scraping supportés
- ✅ Formats supportés
- ✅ Tournois récents avec archétypes
- ✅ Analyse méta
- ✅ Recherche par archétype
- ✅ Scraping de decks
- ✅ APIs CRUD existantes

---

## 🚀 Avantages

### Avant (MVP basique)
- ❌ Pas de scraping automatique
- ❌ Pas de classification d'archétypes
- ❌ Pas de cache de tournois externe
- ✅ Seulement CRUD manuel

### Après (Intégrations réelles)
- ✅ Scraping automatique de 7 sites MTG
- ✅ Classification d'archétypes avec 12 types de conditions
- ✅ Cache de tournois depuis 3 sources
- ✅ Analyse complète du méta
- ✅ Recherche par archétype
- ✅ + CRUD manuel existant

---

## 📈 Performance

- **Cache local** : Évite les appels répétés
- **Scraping asynchrone** : Traitement en parallèle
- **Classification optimisée** : Moteur de règles efficace
- **API REST** : Réponses rapides

---

## 🔮 Évolutions futures

1. **Cache distribué** : Redis pour le cache
2. **Scraping temps réel** : WebSockets pour updates
3. **ML archétypes** : Apprentissage automatique
4. **API rate limiting** : Protection contre abus
5. **Interface graphique** : Dashboard React

---

## 💻 Développement

Pour ajouter un nouveau site de scraping :

```python
def _scrape_nouveau_site(self, url: str) -> Optional[Dict]:
    soup = self._fetch_page(url)
    # Logique de scraping spécifique
    return deck_data
```

Pour ajouter un nouveau format :

```bash
mkdir -p cache/integrations/archetype_formats/NOUVEAU_FORMAT/archetypes
mkdir -p cache/integrations/archetype_formats/NOUVEAU_FORMAT/fallbacks
```

---

## 📞 Support

- **Documentation** : http://localhost:8000/docs
- **Tests** : `./test-integrations.sh`
- **Logs** : Activés par défaut
- **Debug** : Mode développement avec reload

---

## ✅ Résumé

**Objectif atteint** : Intégration complète et réelle des 3 projets GitHub
- 🔄 **Jiliac Cache** : Tournois automatiques
- 🕷️ **MTG Scraper** : Scraping multi-sites
- 🎯 **Badaro Engine** : Classification intelligente

**Pas de fake data** - Que du réel ! 🚀 