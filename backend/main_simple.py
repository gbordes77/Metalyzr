"""
Backend FastAPI simple pour le MVP Metalyzr
Fournit de vraies données depuis MTGODecklistCache + données local
Version sécurisée avec rate limiting et monitoring
"""
import json
import asyncio
import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest

# Import du gestionnaire de cache
from cache_manager import mtgo_cache_manager

# Import du health checker enrichi
try:
    from health_enhanced import health_checker
    HEALTH_ENHANCED_AVAILABLE = True
except ImportError:
    HEALTH_ENHANCED_AVAILABLE = False
    logger.warning("Health checker enrichi non disponible - utilisation basique")

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('metalyzr.log')
    ]
)
logger = logging.getLogger("metalyzr.api")

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)

# Monitoring métriques avec gestion des duplicates
try:
    REQUEST_COUNT = Counter('metalyzr_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
    REQUEST_DURATION = Histogram('metalyzr_request_duration_seconds', 'Request duration')
    CACHE_HITS = Counter('metalyzr_cache_hits_total', 'Cache hits', ['type'])
    API_ERRORS = Counter('metalyzr_api_errors_total', 'API errors', ['error_type'])
except ValueError:
    # Si les métriques existent déjà, les récupérer depuis le registre
    from prometheus_client import CollectorRegistry, REGISTRY
    from prometheus_client.registry import RestrictedRegistry
    
    # Nettoyer le registre pour éviter les conflits
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        if hasattr(collector, '_name') and 'metalyzr' in str(collector._name):
            try:
                REGISTRY.unregister(collector)
            except KeyError:
                pass
    
    # Recréer les métriques
    REQUEST_COUNT = Counter('metalyzr_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
    REQUEST_DURATION = Histogram('metalyzr_request_duration_seconds', 'Request duration')
    CACHE_HITS = Counter('metalyzr_cache_hits_total', 'Cache hits', ['type'])
    API_ERRORS = Counter('metalyzr_api_errors_total', 'API errors', ['error_type'])

app = FastAPI(
    title="Metalyzr API", 
    version="2.0.0",
    description="🎯 MTG Meta Analysis Platform avec cache MTGODecklistCache",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS sécurisée
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://metalyzr.vercel.app",  # Production
    "https://metalyzr.com"  # Custom domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware de monitoring
@app.middleware("http")
async def add_monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Métriques de succès
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        # Log structuré
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": get_remote_address(request)
            }
        )
        
        return response
        
    except Exception as e:
        # Métriques d'erreur
        API_ERRORS.labels(error_type=type(e).__name__).inc()
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "client_ip": get_remote_address(request)
            }
        )
        raise

# Données réelles uniquement - vides au démarrage
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
    logger.info("🚀 Démarrage du backend Metalyzr avec cache MTGODecklistCache...")
    
    try:
        async with mtgo_cache_manager as cache:
            success = await cache.initialize()
            if success:
                logger.info("✅ Cache MTGODecklistCache initialisé avec succès")
                REAL_DATA["stats"]["cache_status"] = "active"
                CACHE_HITS.labels(type="initialization").inc()
                
                # Charger des données depuis le cache
                await load_cache_data()
            else:
                logger.warning("⚠️ Échec d'initialisation du cache, mode fallback activé")
                REAL_DATA["stats"]["cache_status"] = "fallback"
                API_ERRORS.labels(error_type="cache_init_failed").inc()
    except Exception as e:
        logger.error(f"❌ Erreur cache: {e}")
        REAL_DATA["stats"]["cache_status"] = "error"
        API_ERRORS.labels(error_type="cache_error").inc()

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
            
            # Extraire archétypes uniques SEULEMENT s'il y a de vrais decks
            archetype_stats = {}
            total_decks_analyzed = 0
            
            for tournament in all_tournaments:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype", "")
                    if archetype and archetype != "Unknown" and archetype.strip():
                        total_decks_analyzed += 1
                        if archetype not in archetype_stats:
                            archetype_stats[archetype] = {
                                "count": 0,
                                "wins": 0,
                                "total_games": 0
                            }
                        archetype_stats[archetype]["count"] += 1
                        
                        # Calculer vraies stats si disponibles
                        if "wins" in deck:
                            archetype_stats[archetype]["wins"] += deck.get("wins", 0)
                        if "total_games" in deck:
                            archetype_stats[archetype]["total_games"] += deck.get("total_games", 0)
            
            # Créer liste d'archétypes avec vraies statistiques SEULEMENT
            archetype_list = []
            for archetype, stats in archetype_stats.items():
                popularity = (stats["count"] / total_decks_analyzed * 100) if total_decks_analyzed > 0 else 0
                win_rate = (stats["wins"] / stats["total_games"] * 100) if stats["total_games"] > 0 else None
                
                archetype_data = {
                    "id": len(archetype_list) + 1,
                    "name": archetype,
                    "description": f"Archétype détecté dans {stats['count']} deck(s)",
                    "popularity": round(popularity, 2),
                    "deck_count": stats["count"]
                }
                
                # Ajouter winRate SEULEMENT si on a de vraies données
                if win_rate is not None:
                    archetype_data["winRate"] = round(win_rate, 2)
                
                archetype_list.append(archetype_data)
            
            REAL_DATA["archetypes"] = archetype_list
            REAL_DATA["stats"]["archetypes"] = len(archetype_list)
            REAL_DATA["stats"]["lastUpdate"] = datetime.now().isoformat()
            
            CACHE_HITS.labels(type="data_load").inc()
            logger.info(f"📊 Données chargées: {len(all_tournaments)} tournois, {total_decks} decks, {len(archetype_list)} archétypes")
            
    except Exception as e:
        logger.error(f"❌ Erreur chargement cache: {e}")
        API_ERRORS.labels(error_type="cache_load_failed").inc()

# Routes API avec rate limiting et documentation complète

@app.get("/health", 
         summary="Health Check",
         description="Vérifie l'état de santé de l'API et du cache",
         tags=["System"])
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Check système de santé avec status cache"""
    cache_stats = {}
    try:
        async with mtgo_cache_manager as cache:
            cache_stats = await cache.get_cache_stats()
        CACHE_HITS.labels(type="health_check").inc()
    except Exception as e:
        cache_stats = {"error": "Cache unavailable"}
        API_ERRORS.labels(error_type="cache_unavailable").inc()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Metalyzr API is running",
        "cache_status": REAL_DATA["stats"]["cache_status"],
        "cache_info": cache_stats,
        "version": "2.0.0"
    }

@app.get("/health/detailed", 
         summary="Detailed Health Check",
         description="Health check détaillé avec vérification de tous les services externes",
         tags=["System"])
@limiter.limit("10/minute")
async def detailed_health_check(request: Request):
    """Health check enrichi avec vérifications externes"""
    if HEALTH_ENHANCED_AVAILABLE:
        try:
            return await health_checker.comprehensive_health_check()
        except Exception as e:
            logger.error(f"Erreur health check enrichi: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": "Failed to perform detailed health check",
                "fallback": True
            }
    else:
        return {
            "status": "limited",
            "timestamp": datetime.now().isoformat(),
            "message": "Detailed health check not available - missing dependencies",
            "basic_status": "healthy",
            "available_checks": ["basic", "cache"]
        }

@app.get("/metrics", 
         summary="Prometheus Metrics",
         description="Métriques Prometheus pour monitoring",
         tags=["System"])
async def get_metrics():
    """Métriques Prometheus"""
    return generate_latest()

@app.get("/api/stats", 
         summary="Global Statistics",
         description="Statistiques globales de l'application",
         tags=["Analytics"])
@limiter.limit("60/minute")
async def get_stats(request: Request):
    """Statistiques globales en temps réel"""
    cache_stats = {}
    try:
        async with mtgo_cache_manager as cache:
            cache_stats = await cache.get_cache_stats()
        CACHE_HITS.labels(type="stats").inc()
    except Exception as e:
        cache_stats = {}
        API_ERRORS.labels(error_type="stats_error").inc()
    
    return {
        **REAL_DATA["stats"],
        "cache_stats": cache_stats,
        "data_sources": {
            "mtgo_cache": REAL_DATA["stats"]["cache_status"],
            "local": "active",
            "api_status": "healthy"
        }
    }

@app.get("/api/tournaments", 
         summary="List Tournaments",
         description="Liste des tournois disponibles",
         tags=["Tournaments"])
@limiter.limit("100/minute")
async def get_tournaments(request: Request):
    """Liste des tournois depuis le cache + données locales"""
    CACHE_HITS.labels(type="tournaments").inc()
    return REAL_DATA["tournaments"]

@app.get("/api/tournaments/{tournament_id}", 
         summary="Get Tournament Details",
         description="Détails d'un tournoi spécifique",
         tags=["Tournaments"])
@limiter.limit("100/minute")
async def get_tournament_details(tournament_id: int, request: Request):
    """Détails d'un tournoi spécifique"""
    if tournament_id <= len(REAL_DATA["tournaments"]) and tournament_id > 0:
        tournament = REAL_DATA["tournaments"][tournament_id - 1]
        CACHE_HITS.labels(type="tournament_details").inc()
        return tournament
    else:
        API_ERRORS.labels(error_type="tournament_not_found").inc()
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")

@app.get("/api/archetypes", 
         summary="List Archetypes",
         description="Liste des archétypes détectés",
         tags=["Archetypes"])
@limiter.limit("100/minute")
async def get_archetypes(request: Request):
    """Liste des archétypes détectés"""
    CACHE_HITS.labels(type="archetypes").inc()
    return REAL_DATA["archetypes"]

@app.post("/api/tournaments", 
          summary="Create Tournament",
          description="Créer un nouveau tournoi",
          tags=["Tournaments"])
@limiter.limit("10/minute")
async def create_tournament(tournament_data: dict, request: Request):
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
    
    logger.info(f"Nouveau tournoi créé: {tournament['name']}")
    return tournament

@app.post("/api/archetypes", 
          summary="Create Archetype",
          description="Créer un nouvel archétype",
          tags=["Archetypes"])
@limiter.limit("10/minute")
async def create_archetype(archetype_data: dict, request: Request):
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
    
    logger.info(f"Nouvel archétype créé: {archetype['name']}")
    return archetype



@app.get("/api/cache/sync", 
         summary="Sync Cache",
         description="Forcer une synchronisation du cache",
         tags=["Cache"])
@limiter.limit("3/minute")
async def sync_cache(request: Request):
    """Forcer une synchronisation du cache"""
    try:
        async with mtgo_cache_manager as cache:
            success = await cache.sync_from_remote()
            if success:
                await load_cache_data()
                CACHE_HITS.labels(type="sync_success").inc()
                logger.info("Cache synchronisé avec succès")
                return {
                    "status": "success",
                    "message": "Cache synchronisé avec succès",
                    "stats": REAL_DATA["stats"]
                }
            else:
                API_ERRORS.labels(error_type="sync_failed").inc()
                return {
                    "status": "error", 
                    "message": "Échec de synchronisation"
                }
    except Exception as e:
        API_ERRORS.labels(error_type="sync_exception").inc()
        logger.error(f"Erreur sync cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur sync: {str(e)}")

@app.get("/api/cache/status", 
         summary="Cache Status",
         description="Status détaillé du cache",
         tags=["Cache"])
@limiter.limit("20/minute")
async def cache_status(request: Request):
    """Status détaillé du cache"""
    try:
        async with mtgo_cache_manager as cache:
            stats = await cache.get_cache_stats()
            CACHE_HITS.labels(type="status").inc()
            return {
                "cache_status": REAL_DATA["stats"]["cache_status"],
                "detailed_stats": stats,
                "last_loaded": REAL_DATA["stats"]["lastUpdate"]
            }
    except Exception as e:
        API_ERRORS.labels(error_type="status_error").inc()
        return {
            "cache_status": "error",
            "error": str(e)
        }

@app.get("/", 
         summary="API Information",
         description="Page d'accueil de l'API",
         tags=["System"])
async def root():
    """Page d'accueil API"""
    return {
        "message": "Metalyzr API - Backend avec Cache MTGODecklistCache",
        "version": "2.0.0", 
        "status": "running",
        "cache_status": REAL_DATA["stats"]["cache_status"],
        "features": [
            "Rate limiting activé",
            "Monitoring Prometheus",
            "Cache MTGODecklistCache",
            "Logging structuré",
            "Documentation OpenAPI"
        ],
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "stats": "/api/stats", 
            "tournaments": "/api/tournaments",
            "archetypes": "/api/archetypes",
            "cache": "/api/cache/sync"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Démarrage du backend Metalyzr sécurisé...")
    logger.info("📊 API disponible sur http://localhost:8000")
    logger.info("🏥 Health check: http://localhost:8000/health")
    logger.info("📈 Stats: http://localhost:8000/api/stats")
    logger.info("💾 Cache sync: http://localhost:8000/api/cache/sync")
    logger.info("📊 Metrics: http://localhost:8000/metrics")
    logger.info("📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_simple:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 