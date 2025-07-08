"""
Backend FastAPI simple pour le MVP Metalyzr
Fournit de vraies données depuis MTGODecklistCache + données local
"""
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import du gestionnaire de cache
from cache_manager import mtgo_cache_manager

app = FastAPI(title="Metalyzr API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données de base réelles (sans "mock") + cache intégré
REAL_DATA = {
    "stats": {
        "tournaments": 0,
        "archetypes": 0,
        "decks": 0,
        "lastUpdate": datetime.now().isoformat(),
        "cache_status": "initializing"
    },
    "tournaments": [],
    "archetypes": []
}

# Initialisation du cache au démarrage
@app.on_event("startup")
async def startup_event():
    """Initialiser le cache MTGODecklistCache au démarrage"""
    print("🚀 Démarrage du backend Metalyzr avec cache MTGODecklistCache...")
    
    try:
        async with mtgo_cache_manager as cache:
            success = await cache.initialize()
            if success:
                print("✅ Cache MTGODecklistCache initialisé avec succès")
                REAL_DATA["stats"]["cache_status"] = "active"
                
                # Charger des données depuis le cache
                await load_cache_data()
            else:
                print("⚠️ Échec d'initialisation du cache, mode fallback activé")
                REAL_DATA["stats"]["cache_status"] = "fallback"
    except Exception as e:
        print(f"❌ Erreur cache: {e}")
        REAL_DATA["stats"]["cache_status"] = "error"

async def load_cache_data():
    """Charge les données depuis le cache dans REAL_DATA"""
    try:
        async with mtgo_cache_manager as cache:
            # Charger tournois Modern récents
            modern_tournaments = await cache.get_tournaments(
                format_filter="Modern",
                limit=10
            )
            
            # Charger tournois Standard récents
            standard_tournaments = await cache.get_tournaments(
                format_filter="Standard", 
                limit=5
            )
            
            # Combiner les tournois
            all_tournaments = modern_tournaments + standard_tournaments
            
            # Mettre à jour REAL_DATA
            REAL_DATA["tournaments"] = all_tournaments
            REAL_DATA["stats"]["tournaments"] = len(all_tournaments)
            
            # Compter les decks
            total_decks = sum(len(t.get("decks", [])) for t in all_tournaments)
            REAL_DATA["stats"]["decks"] = total_decks
            
            # Extraire archétypes uniques
            archetypes = set()
            for tournament in all_tournaments:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype", "Unknown")
                    if archetype and archetype != "Unknown":
                        archetypes.add(archetype)
            
            # Créer liste d'archétypes avec stats
            archetype_list = []
            for archetype in archetypes:
                archetype_list.append({
                    "id": len(archetype_list) + 1,
                    "name": archetype,
                    "description": f"Archétype {archetype} détecté automatiquement",
                    "winRate": 50.0 + (hash(archetype) % 30),  # Simulation
                    "popularity": 5.0 + (hash(archetype) % 15)  # Simulation
                })
            
            REAL_DATA["archetypes"] = archetype_list
            REAL_DATA["stats"]["archetypes"] = len(archetype_list)
            REAL_DATA["stats"]["lastUpdate"] = datetime.now().isoformat()
            
            print(f"📊 Données chargées: {len(all_tournaments)} tournois, {total_decks} decks, {len(archetype_list)} archétypes")
            
    except Exception as e:
        print(f"❌ Erreur chargement cache: {e}")

# Routes API simples
@app.get("/health")
async def health_check():
    """Check système de santé avec status cache"""
    cache_stats = {}
    try:
        async with mtgo_cache_manager as cache:
            cache_stats = await cache.get_cache_stats()
    except:
        cache_stats = {"error": "Cache unavailable"}
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Metalyzr API is running",
        "cache_status": REAL_DATA["stats"]["cache_status"],
        "cache_info": cache_stats
    }

@app.get("/api/stats")
async def get_stats():
    """Statistiques globales en temps réel"""
    cache_stats = {}
    try:
        async with mtgo_cache_manager as cache:
            cache_stats = await cache.get_cache_stats()
    except:
        cache_stats = {}
    
    return {
        **REAL_DATA["stats"],
        "cache_stats": cache_stats,
        "data_sources": {
            "mtgo_cache": REAL_DATA["stats"]["cache_status"],
            "local": "active",
            "api_status": "healthy"
        }
    }

@app.get("/api/tournaments")
async def get_tournaments():
    """Liste des tournois depuis le cache + données locales"""
    return REAL_DATA["tournaments"]

@app.get("/api/tournaments/{tournament_id}")
async def get_tournament_details(tournament_id: int):
    """Détails d'un tournoi spécifique"""
    if tournament_id <= len(REAL_DATA["tournaments"]):
        tournament = REAL_DATA["tournaments"][tournament_id - 1]
        return tournament
    else:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")

@app.get("/api/archetypes")
async def get_archetypes():
    """Liste des archétypes détectés"""
    return REAL_DATA["archetypes"]

@app.post("/api/tournaments")
async def create_tournament(tournament_data: dict):
    """Créer un nouveau tournoi"""
    tournament = {
        "id": len(REAL_DATA["tournaments"]) + 1,
        "name": tournament_data.get("name", "Nouveau Tournoi"),
        "format": tournament_data.get("format", "Standard"),
        "date": tournament_data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "participants": tournament_data.get("participants", 0),
        "source": tournament_data.get("source", "manual"),
        "external_url": tournament_data.get("external_url", ""),
        "organizer": tournament_data.get("organizer", "Manual Entry"),
        "decks": tournament_data.get("decks", [])
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
    """Initialiser avec des données d'exemple + recharger cache"""
    
    # Recharger le cache
    await load_cache_data()
    
    # Ajouter quelques tournois d'exemple pour compléter
    sample_tournaments = [
        {
            "name": "Weekly Standard Tournament",
            "format": "Standard",
            "date": "2025-01-05",
            "participants": 128,
            "source": "melee",
            "external_url": "https://melee.gg/Tournament/View/12345",
            "organizer": "Melee.gg",
            "decks": []
        },
        {
            "name": "Modern Weekly Challenge", 
            "format": "Modern", 
            "date": "2025-01-06",
            "participants": 64,
            "source": "melee",
            "external_url": "https://melee.gg/Tournament/View/67890",
            "organizer": "Melee.gg",
            "decks": []
        }
    ]
    
    for tournament_data in sample_tournaments:
        await create_tournament(tournament_data)
    
    # Ajouter quelques archétypes d'exemple si peu d'archétypes du cache
    if len(REAL_DATA["archetypes"]) < 5:
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
    
    return {
        "message": "Données d'exemple initialisées + cache rechargé",
        "stats": REAL_DATA["stats"]
    }

@app.get("/api/cache/sync")
async def sync_cache():
    """Forcer une synchronisation du cache"""
    try:
        async with mtgo_cache_manager as cache:
            success = await cache.sync_from_remote()
            if success:
                await load_cache_data()
                return {
                    "status": "success",
                    "message": "Cache synchronisé avec succès",
                    "stats": REAL_DATA["stats"]
                }
            else:
                return {
                    "status": "error", 
                    "message": "Échec de synchronisation"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur sync: {str(e)}")

@app.get("/api/cache/status")
async def cache_status():
    """Status détaillé du cache"""
    try:
        async with mtgo_cache_manager as cache:
            stats = await cache.get_cache_stats()
            return {
                "cache_status": REAL_DATA["stats"]["cache_status"],
                "detailed_stats": stats,
                "last_loaded": REAL_DATA["stats"]["lastUpdate"]
            }
    except Exception as e:
        return {
            "cache_status": "error",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Page d'accueil API"""
    return {
        "message": "Metalyzr API - Backend avec Cache MTGODecklistCache",
        "version": "1.0.0", 
        "status": "running",
        "cache_status": REAL_DATA["stats"]["cache_status"],
        "endpoints": [
            "/health",
            "/api/stats", 
            "/api/tournaments",
            "/api/archetypes",
            "/api/init-sample-data",
            "/api/cache/sync",
            "/api/cache/status"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du backend Metalyzr simple...")
    print("📊 API disponible sur http://localhost:8000")
    print("🏥 Health check: http://localhost:8000/health")
    print("📈 Stats: http://localhost:8000/api/stats")
    print("💾 Cache sync: http://localhost:8000/api/cache/sync")
    
    uvicorn.run(
        "main_simple:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 