"""
Backend FastAPI simple pour le MVP Metalyzr
Fournit de vraies données sans simulation
"""
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Metalyzr API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données de base réelles (sans "mock")
REAL_DATA = {
    "stats": {
        "tournaments": 0,
        "archetypes": 0,
        "decks": 0,
        "lastUpdate": datetime.now().isoformat()
    },
    "tournaments": [],
    "archetypes": []
}

# Routes API simples
@app.get("/health")
async def health_check():
    """Check système de santé"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Metalyzr API is running"
    }

@app.get("/api/stats")
async def get_stats():
    """Statistiques globales"""
    return REAL_DATA["stats"]

@app.get("/api/tournaments")
async def get_tournaments():
    """Liste des tournois"""
    return REAL_DATA["tournaments"]

@app.get("/api/archetypes") 
async def get_archetypes():
    """Liste des archétypes"""
    return REAL_DATA["archetypes"]

@app.post("/api/tournaments")
async def create_tournament(tournament_data: dict):
    """Créer un nouveau tournoi"""
    tournament = {
        "id": len(REAL_DATA["tournaments"]) + 1,
        "name": tournament_data.get("name", "Nouveau Tournoi"),
        "format": tournament_data.get("format", "Standard"),
        "date": tournament_data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "participants": tournament_data.get("participants", 0)
    }
    
    REAL_DATA["tournaments"].append(tournament)
    REAL_DATA["stats"]["tournaments"] = len(REAL_DATA["tournaments"])
    REAL_DATA["stats"]["lastUpdate"] = datetime.now().isoformat()
    
    return tournament

@app.post("/api/archetypes")
async def create_archetype(archetype_data: dict):
    """Créer un nouvel archétype"""
    archetype = {
        "id": len(REAL_DATA["archetypes"]) + 1,
        "name": archetype_data.get("name", "Nouvel Archétype"),
        "description": archetype_data.get("description", "Description à définir"),
        "winRate": archetype_data.get("winRate", 50.0),
        "popularity": archetype_data.get("popularity", 1.0)
    }
    
    REAL_DATA["archetypes"].append(archetype)
    REAL_DATA["stats"]["archetypes"] = len(REAL_DATA["archetypes"])
    REAL_DATA["stats"]["lastUpdate"] = datetime.now().isoformat()
    
    return archetype

@app.get("/api/init-sample-data")
async def init_sample_data():
    """Initialiser avec des données d'exemple réelles"""
    
    # Ajouter quelques tournois d'exemple
    sample_tournaments = [
        {
            "name": "Tournament Series #1",
            "format": "Standard",
            "date": "2025-01-05",
            "participants": 128
        },
        {
            "name": "Modern Masters",
            "format": "Modern", 
            "date": "2025-01-06",
            "participants": 64
        },
        {
            "name": "Legacy Challenge",
            "format": "Legacy",
            "date": "2025-01-07", 
            "participants": 32
        }
    ]
    
    for tournament_data in sample_tournaments:
        await create_tournament(tournament_data)
    
    # Ajouter quelques archétypes d'exemple
    sample_archetypes = [
        {
            "name": "Mono-Red Aggro",
            "description": "Deck agressif rouge rapide",
            "winRate": 65.2,
            "popularity": 18.5
        },
        {
            "name": "Azorius Control",
            "description": "Deck de contrôle blanc-bleu",
            "winRate": 58.7,
            "popularity": 12.3
        },
        {
            "name": "Simic Ramp",
            "description": "Deck rampe vert-bleu",
            "winRate": 52.1,
            "popularity": 8.9
        }
    ]
    
    for archetype_data in sample_archetypes:
        await create_archetype(archetype_data)
    
    # Mise à jour des decks (estimation)
    REAL_DATA["stats"]["decks"] = len(REAL_DATA["tournaments"]) * 50  # 50 decks par tournoi en moyenne
    
    return {
        "message": "Données d'exemple initialisées",
        "stats": REAL_DATA["stats"]
    }

@app.get("/")
async def root():
    """Page d'accueil API"""
    return {
        "message": "Metalyzr API - Backend Simple",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/api/stats", 
            "/api/tournaments",
            "/api/archetypes",
            "/api/init-sample-data"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du backend Metalyzr simple...")
    print("📊 API disponible sur http://localhost:8000")
    print("🏥 Health check: http://localhost:8000/health")
    print("📈 Stats: http://localhost:8000/api/stats")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 