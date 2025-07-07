# 🏗️ METALYZR - Architecture et Guide Complet

## 📋 Table des Matières

1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Architecture système](#architecture-système)
3. [Infrastructure Docker](#infrastructure-docker)
4. [Backend FastAPI](#backend-fastapi)
5. [Base de données PostgreSQL](#base-de-données-postgresql)
6. [Scraper MTGTop8](#scraper-mtgtop8)
7. [Frontend React](#frontend-react)
8. [APIs et Endpoints](#apis-et-endpoints)
9. [Guide de débogage](#guide-de-débogage)
10. [Déploiement et utilisation](#déploiement-et-utilisation)

---

## 🎯 Vue d'ensemble du projet

**Metalyzr** est une plateforme d'analyse du métagame Magic: The Gathering qui collecte, analyse et visualise les données de tournois pour aider les joueurs à comprendre les tendances du jeu compétitif.

### Objectifs principaux :
- 📊 **Analyse du métagame** : Visualisation des archétypes dominants
- 🏆 **Suivi des tournois** : Collecte automatisée des résultats
- 📈 **Tendances** : Évolution des performances des decks
- 🎯 **Intelligence compétitive** : Aide à la prise de décision pour les joueurs

### Technologies utilisées :
- **Backend** : Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **Frontend** : React 18, TypeScript, Tailwind CSS, Recharts
- **Base de données** : PostgreSQL 15
- **Cache** : Redis 7
- **Scraping** : aiohttp, BeautifulSoup4
- **Containerisation** : Docker, Docker Compose

---

## 🏛️ Architecture système

```mermaid
graph TB
    subgraph "🌐 Frontend Layer"
        FE[React Dashboard<br/>TypeScript + Tailwind]
        FE_PUB[Public Dashboard<br/>Métagame & Tournois]
        FE_ADMIN[Admin Dashboard<br/>Monitoring & Config]
        FE_DETAIL[Tournament Details<br/>Analyses détaillées]
    end

    subgraph "🔌 API Layer"
        API[FastAPI Backend<br/>Python 3.11]
        AUTH[Authentication<br/>JWT Tokens]
        DOCS[Swagger/OpenAPI<br/>Documentation]
    end

    subgraph "💾 Data Layer"
        DB[(PostgreSQL 15<br/>Données principales)]
        REDIS[(Redis 7<br/>Cache & Sessions)]
    end

    subgraph "🕷️ Data Collection"
        SCRAPER[MTGTop8 Scraper<br/>aiohttp + BeautifulSoup]
        SCHEDULER[Task Scheduler<br/>Collecte automatisée]
    end

    subgraph "🐳 Infrastructure"
        DOCKER[Docker Compose<br/>Orchestration]
        NGINX[Nginx<br/>Reverse Proxy]
    end

    FE --> FE_PUB
    FE --> FE_ADMIN
    FE --> FE_DETAIL
    
    FE_PUB --> API
    FE_ADMIN --> API
    FE_DETAIL --> API
    
    API --> AUTH
    API --> DOCS
    API --> DB
    API --> REDIS
    
    SCRAPER --> DB
    SCHEDULER --> SCRAPER
    
    DOCKER --> API
    DOCKER --> DB
    DOCKER --> REDIS
    DOCKER --> SCRAPER
```

### Flux de données principal :

1. **📥 Collecte** : Scraper → MTGTop8 → Base de données
2. **🔄 Traitement** : Backend → Analyse → Cache Redis
3. **📊 API** : FastAPI → Endpoints REST → Frontend
4. **🎨 Visualisation** : React → Graphiques → Utilisateur

---

## 🐳 Infrastructure Docker

### Architecture conteneurisée :

```yaml
services:
  backend:          # FastAPI + Python
  postgres:         # Base de données principale
  redis:           # Cache et sessions
  scraper:         # Collecteur de données
  frontend:        # Interface React (développement)
```

### Fichier docker-compose.yml :

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://metalyzr:password@postgres:5432/metalyzr
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: metalyzr
      POSTGRES_USER: metalyzr
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U metalyzr"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  scraper:
    build: ./scraper
    environment:
      - DATABASE_URL=postgresql://metalyzr:password@postgres:5432/metalyzr
      - SCRAPER_DELAY=300
      - MAX_TOURNAMENTS_PER_RUN=50
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

### Commandes Docker essentielles :

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état des conteneurs
docker-compose ps

# Voir les logs d'un service
docker-compose logs backend

# Redémarrer un service
docker-compose restart backend

# Arrêter tous les services
docker-compose down

# Reconstruction complète
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## ⚡ Backend FastAPI

### Structure du projet :

```
backend/
├── main.py                 # Point d'entrée FastAPI
├── database.py            # Configuration SQLAlchemy
├── init_db.py             # Script d'initialisation
├── models/                # Modèles de données
│   ├── __init__.py
│   ├── tournament.py      # Modèle Tournament
│   ├── deck.py           # Modèle Deck
│   ├── card.py           # Modèle Card
│   └── archetype.py      # Modèle Archetype
├── api/                  # Routes API
│   ├── __init__.py
│   ├── tournaments.py    # Endpoints tournois
│   └── archetypes.py     # Endpoints archétypes
├── requirements.txt      # Dépendances Python
└── Dockerfile           # Configuration Docker
```

### Configuration principale (main.py) :

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.tournaments import router as tournaments_router
from api.archetypes import router as archetypes_router
from database import engine
from models import Base

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Metalyzr API",
    description="API pour l'analyse du métagame Magic: The Gathering",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(tournaments_router, prefix="/api/tournaments", tags=["tournaments"])
app.include_router(archetypes_router, prefix="/api/archetypes", tags=["archetypes"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "metalyzr-api"}
```

### Modèles de données principaux :

#### Tournament
```python
class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    format = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String)
    organizer = Column(String)
    tournament_type = Column(String)
    total_players = Column(Integer)
    rounds = Column(Integer)
    is_complete = Column(Boolean, default=False)
    source_site = Column(String)
    source_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    decks = relationship("Deck", back_populates="tournament", cascade="all, delete-orphan")
```

#### Deck
```python
class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, nullable=False)
    position = Column(Integer)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    mainboard = Column(JSON)
    sideboard = Column(JSON)
    archetype_id = Column(Integer, ForeignKey("archetypes.id"))
    archetype_confidence = Column(Float)
    manual_archetype = Column(String)
    color_identity = Column(String)
    mana_curve = Column(JSON)
    total_cards = Column(Integer, default=0)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    tournament = relationship("Tournament", back_populates="decks")
    archetype = relationship("Archetype", back_populates="decks")
```

---

## 🗄️ Base de données PostgreSQL

### Schéma relationnel :

```mermaid
erDiagram
    TOURNAMENT ||--o{ DECK : "has many"
    ARCHETYPE ||--o{ DECK : "categorizes"
    ARCHETYPE ||--o{ DETECTION_RULE : "has rules"
    CARD ||--o{ CARD_POPULARITY : "tracked in"
    
    TOURNAMENT {
        int id PK
        string name
        string format
        datetime date
        string location
        string organizer
        int total_players
        int rounds
        boolean is_complete
        string source_site
        datetime created_at
    }
    
    DECK {
        int id PK
        string player_name
        int position
        int wins
        int losses
        int draws
        json mainboard
        json sideboard
        int archetype_id FK
        float archetype_confidence
        string color_identity
        int tournament_id FK
        datetime created_at
    }
    
    ARCHETYPE {
        int id PK
        string name
        string format
        string category
        string description
        string color_identity
        json key_cards
        json variations
        datetime created_at
    }
    
    DETECTION_RULE {
        int id PK
        int archetype_id FK
        string rule_type
        json conditions
        float weight
        boolean is_active
    }
    
    CARD {
        int id PK
        string name
        string mana_cost
        string type_line
        text oracle_text
        string rarity
        string set_code
    }
    
    CARD_POPULARITY {
        int id PK
        int card_id FK
        string format
        int play_count
        float meta_percentage
        datetime last_updated
    }
```

### Script d'initialisation (init_db.py) :

```python
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Tournament, Deck, Archetype, DetectionRule

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_sample_data():
    db = SessionLocal()
    try:
        # Vérifier si des données existent déjà
        if db.query(Tournament).first():
            print("✅ Base de données déjà initialisée")
            return
        
        print("🚀 Initialisation de la base de données...")
        
        # Créer des archétypes d'exemple
        archetypes = [
            Archetype(
                name="Mono-Red Aggro",
                format="Standard",
                category="Aggro",
                description="Deck agressif mono-rouge",
                color_identity="R",
                key_cards=["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"]
            ),
            # ... autres archétypes
        ]
        
        db.add_all(archetypes)
        db.commit()
        
        # Créer un tournoi d'exemple
        tournament = Tournament(
            name="Standard Challenge #12345",
            format="Standard",
            date=datetime(2024, 1, 15),
            location="Magic Online",
            organizer="Wizards of the Coast",
            tournament_type="Challenge",
            total_players=128,
            rounds=7,
            is_complete=True,
            source_site="MTGTop8"
        )
        
        db.add(tournament)
        db.commit()
        
        print("✅ Données d'exemple créées avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        db.rollback()
    finally:
        db.close()
```

---

## 🕷️ Scraper MTGTop8

### Architecture du scraper :

```
scraper/
├── main.py              # Point d'entrée
├── config.py           # Configuration
├── base_scraper.py     # Classe de base abstraite
├── mtgtop8_scraper.py  # Implémentation MTGTop8
├── data_manager.py     # Gestion des données
├── models.py          # Modèles Pydantic
├── requirements.txt   # Dépendances
└── Dockerfile        # Configuration Docker
```

### Scraper principal (mtgtop8_scraper.py) :

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from base_scraper import BaseScraper

class MTGTop8Scraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mtgtop8.com"
        self.session_timeout = aiohttp.ClientTimeout(total=30)
    
    async def scrape_tournaments(self, format_name: str, limit: int = 50):
        """Scraper les tournois d'un format donné"""
        tournaments = []
        
        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            # Récupérer la liste des tournois
            search_url = f"{self.base_url}/search"
            params = {
                'format': format_name,
                'current_page': 1
            }
            
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Parser les tournois
                    tournament_links = soup.find_all('a', class_='tournament-link')
                    
                    for link in tournament_links[:limit]:
                        tournament_data = await self.scrape_tournament_details(
                            session, link['href']
                        )
                        if tournament_data:
                            tournaments.append(tournament_data)
                        
                        # Rate limiting
                        await asyncio.sleep(self.request_delay)
        
        return tournaments
    
    async def scrape_tournament_details(self, session, tournament_url):
        """Scraper les détails d'un tournoi spécifique"""
        try:
            async with session.get(f"{self.base_url}{tournament_url}") as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extraire les informations du tournoi
                    tournament_data = self.parse_tournament_info(soup)
                    
                    # Extraire les decks
                    decks = self.parse_tournament_decks(soup)
                    tournament_data['decks'] = decks
                    
                    return tournament_data
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping de {tournament_url}: {e}")
            return None
```

### Configuration (config.py) :

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Base de données
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://metalyzr:password@localhost:5432/metalyzr"
    )
    
    # Scraper
    scraper_delay: float = float(os.getenv("SCRAPER_DELAY", "2.0"))
    max_tournaments_per_run: int = int(os.getenv("MAX_TOURNAMENTS_PER_RUN", "50"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    timeout_seconds: int = int(os.getenv("TIMEOUT_SECONDS", "30"))
    
    # Formats supportés
    supported_formats: list = [
        "Standard", "Modern", "Legacy", "Vintage", "Pioneer", "Pauper"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## ⚛️ Frontend React

### Structure du projet :

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/           # Composants réutilisables
│   │   ├── ui/              # Composants UI de base
│   │   │   ├── Card.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── MetagameChart.tsx    # Graphiques métagame
│   │   └── TournamentCard.tsx   # Carte de tournoi
│   ├── hooks/               # Hooks personnalisés
│   │   └── useApi.ts       # Hooks pour l'API
│   ├── pages/              # Pages principales
│   │   ├── public/
│   │   │   ├── PublicDashboard.tsx
│   │   │   └── TournamentDetails.tsx
│   │   └── admin/
│   │       └── AdminDashboard.tsx
│   ├── services/           # Services
│   │   └── api.ts         # Client API
│   ├── App.tsx            # Composant principal
│   ├── index.tsx          # Point d'entrée
│   └── index.css          # Styles globaux
├── package.json           # Dépendances npm
├── tailwind.config.js     # Configuration Tailwind
└── tsconfig.json         # Configuration TypeScript
```

### Service API (services/api.ts) :

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Tournament {
  id: number;
  name: string;
  format: string;
  date: string;
  location: string;
  total_players: number;
  rounds: number;
  is_complete: boolean;
}

class ApiService {
  private async fetchApi<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Tournaments
  async getTournaments(params?: {
    format?: string;
    limit?: number;
    offset?: number;
  }): Promise<Tournament[]> {
    const searchParams = new URLSearchParams();
    if (params?.format) searchParams.set('format', params.format);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    
    const query = searchParams.toString();
    return this.fetchApi(`/api/tournaments/${query ? `?${query}` : ''}`);
  }
  
  // ... autres méthodes
}

export const apiService = new ApiService();
```

### Hooks personnalisés (hooks/useApi.ts) :

```typescript
import { useState, useEffect } from 'react';
import { apiService, Tournament } from '../services/api';

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTournaments(params?: {
  format?: string;
  limit?: number;
  offset?: number;
}): UseApiState<Tournament[]> {
  const [data, setData] = useState<Tournament[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const tournaments = await apiService.getTournaments(params);
      setData(tournaments);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params?.format, params?.limit, params?.offset]);

  return { data, loading, error, refetch: fetchData };
}
```

### Composant Dashboard (pages/public/PublicDashboard.tsx) :

```typescript
const PublicDashboard: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [chartType, setChartType] = useState<'pie' | 'bar'>('pie');

  const { data: tournaments, loading: tournamentsLoading, error: tournamentsError } = useTournaments({
    format: selectedFormat || undefined,
    limit: 6
  });

  const { data: archetypes, loading: archetypesLoading, error: archetypesError } = useArchetypes({
    format: selectedFormat || undefined
  });

  // Préparer les données du métagame pour le graphique
  const metagameData = archetypes?.map(archetype => ({
    archetype: archetype.name,
    category: archetype.category,
    deck_count: archetype.deck_count,
    meta_share: archetypes.length > 0 
      ? (archetype.deck_count / archetypes.reduce((sum, a) => sum + a.deck_count, 0)) * 100 
      : 0,
    avg_wins: 0,
    best_position: null
  })).filter(entry => entry.deck_count > 0) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec filtres */}
      {/* Statistiques rapides */}
      {/* Graphiques métagame */}
      {/* Liste des tournois */}
      {/* Archétypes populaires */}
    </div>
  );
};
```

---

## 🔌 APIs et Endpoints

### Endpoints disponibles :

#### 🏆 Tournois
```http
GET /api/tournaments/                    # Liste des tournois
GET /api/tournaments/{id}/               # Détails d'un tournoi
GET /api/tournaments/{id}/metagame/      # Métagame du tournoi
GET /api/tournaments/{id}/decks/         # Decks du tournoi
```

#### 🎯 Archétypes
```http
GET /api/archetypes/                     # Liste des archétypes
GET /api/archetypes/{id}/                # Détails d'un archétype
GET /api/archetypes/{id}/decks/          # Decks utilisant cet archétype
```

#### 🏥 Santé
```http
GET /health                              # État de l'API
```

### Exemples de réponses :

#### GET /api/tournaments/
```json
[
  {
    "id": 1,
    "name": "Standard Challenge #12345",
    "format": "Standard",
    "date": "2024-01-15T00:00:00",
    "location": "Magic Online",
    "total_players": 128,
    "rounds": 7,
    "is_complete": true
  }
]
```

#### GET /api/tournaments/1/metagame/
```json
{
  "tournament_id": 1,
  "tournament_name": "Standard Challenge #12345",
  "total_decks": 128,
  "metagame": [
    {
      "archetype": "Mono-Red Aggro",
      "category": "Aggro",
      "deck_count": 32,
      "meta_share": 25.0,
      "avg_wins": 4.2,
      "best_position": 1
    }
  ]
}
```

### Paramètres de requête :

#### Tournois
- `format` : Filtrer par format (Standard, Modern, etc.)
- `limit` : Nombre maximum de résultats
- `offset` : Décalage pour la pagination

#### Archétypes
- `format` : Filtrer par format
- `category` : Filtrer par catégorie (Aggro, Control, etc.)

---

## 🐛 Guide de débogage

### Problèmes courants et solutions :

#### 1. **Erreur de connexion à la base de données**
```bash
# Vérifier l'état de PostgreSQL
docker logs metalyzr_postgres

# Tester la connexion
docker exec -it metalyzr_postgres psql -U metalyzr -d metalyzr -c "SELECT 1;"

# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d postgres
docker exec -it metalyzr-backend-1 python init_db.py
```

#### 2. **API ne répond pas**
```bash
# Vérifier les logs du backend
docker logs metalyzr-backend-1

# Tester l'endpoint de santé
curl http://localhost:8000/health

# Redémarrer le backend
docker-compose restart backend
```

#### 3. **Frontend ne charge pas les données**
```bash
# Vérifier la configuration CORS
curl -H "Origin: http://localhost:3000" http://localhost:8000/api/tournaments/

# Vérifier la variable d'environnement
echo $REACT_APP_API_URL

# Vérifier les logs du navigateur (F12 > Console)
```

#### 4. **Scraper ne fonctionne pas**
```bash
# Vérifier les logs du scraper
docker logs metalyzr-scraper-1

# Tester manuellement
docker exec -it metalyzr-scraper-1 python main.py --format Standard --limit 5

# Vérifier la connectivité réseau
docker exec -it metalyzr-scraper-1 ping mtgtop8.com
```

### Commandes de diagnostic :

```bash
# État général du système
docker-compose ps
docker system df
docker stats

# Logs en temps réel
docker-compose logs -f backend
docker-compose logs -f scraper

# Inspection des conteneurs
docker inspect metalyzr-backend-1
docker exec -it metalyzr-backend-1 /bin/bash

# Base de données
docker exec -it metalyzr_postgres psql -U metalyzr -d metalyzr
\dt                    # Lister les tables
\d tournaments         # Décrire une table
SELECT COUNT(*) FROM tournaments;
```

### Variables d'environnement importantes :

```bash
# Backend
DATABASE_URL=postgresql://metalyzr:password@postgres:5432/metalyzr
REDIS_URL=redis://redis:6379
CORS_ORIGINS=["http://localhost:3000"]

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Scraper
SCRAPER_DELAY=2.0
MAX_TOURNAMENTS_PER_RUN=50
TIMEOUT_SECONDS=30
```

---

## 🚀 Déploiement et utilisation

### Démarrage rapide :

```bash
# 1. Cloner le projet
git clone <repository-url>
cd metalyzr

# 2. Démarrer l'infrastructure
docker-compose up -d

# 3. Initialiser la base de données
docker exec -it metalyzr-backend-1 python init_db.py

# 4. Démarrer le frontend (développement)
cd frontend
npm install
npm start

# 5. Accéder aux interfaces
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Admin: http://localhost:3000/admin
# Documentation: http://localhost:8000/docs
```

### Workflow de développement :

```bash
# Développement backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Développement frontend
cd frontend
npm start

# Tests
docker exec -it metalyzr-backend-1 python -m pytest
cd frontend && npm test

# Linting
docker exec -it metalyzr-backend-1 flake8 .
cd frontend && npm run lint
```

### Collecte de données :

```bash
# Lancer le scraper manuellement
docker exec -it metalyzr-scraper-1 python main.py --format Standard --limit 20

# Voir les statistiques
docker exec -it metalyzr-scraper-1 python main.py --stats-only

# Nettoyer les données anciennes
docker exec -it metalyzr-scraper-1 python main.py --cleanup --days 90
```

### Sauvegarde et restauration :

```bash
# Sauvegarde de la base de données
docker exec -t metalyzr_postgres pg_dump -U metalyzr metalyzr > backup.sql

# Restauration
docker exec -i metalyzr_postgres psql -U metalyzr metalyzr < backup.sql

# Export des données
curl http://localhost:8000/api/tournaments/ > tournaments.json
curl http://localhost:8000/api/archetypes/ > archetypes.json
```

---

## 📊 État actuel du projet

### ✅ Fonctionnalités implémentées :

1. **Infrastructure complète** avec Docker Compose
2. **Backend FastAPI** avec 8 endpoints fonctionnels
3. **Base de données PostgreSQL** avec 6 tables relationnelles
4. **Scraper MTGTop8** avec collecte automatisée
5. **Frontend React** avec dashboard complet
6. **Visualisations** avec graphiques interactifs
7. **Navigation** entre pages et détails des tournois
8. **Dashboard admin** avec monitoring
9. **Gestion d'erreurs** et états de chargement
10. **Documentation** API avec Swagger

### 🔄 Flux de données validé :

- **Scraper** → **PostgreSQL** → **FastAPI** → **React** → **Utilisateur**
- **Admin** → **Actions** → **Backend** → **Mise à jour temps réel**

### 🌐 URLs accessibles :

- **Frontend Public** : http://localhost:3000
- **Frontend Admin** : http://localhost:3000/admin
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Base de données** : localhost:5432 (metalyzr/password)

---

**Metalyzr est maintenant une plateforme complète et fonctionnelle pour l'analyse du métagame Magic: The Gathering !** 🎉 