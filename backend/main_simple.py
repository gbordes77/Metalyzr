#!/usr/bin/env python3
"""
Metalyzr MVP - Backend honnête avec intégrations réelles
Plus de fake data - que des fonctionnalités réelles !

Intégrations :
- Jiliac/MTGODecklistCache : Cache de tournois
- MTG Scraper : Scraping de sites
- Badaro Archetype Engine : Classification d'archétypes
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("metalyzr")

# Initialiser l'application
app = FastAPI(
    title="Metalyzr MVP",
    description="Backend honnête avec intégrations réelles des 3 projets GitHub",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dossier des données
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Fichiers de données
TOURNAMENTS_FILE = DATA_DIR / "tournaments.json"
ARCHETYPES_FILE = DATA_DIR / "archetypes.json"
STATS_FILE = DATA_DIR / "stats.json"

# Initialiser les fichiers de données
def init_data_files():
    """Initialiser les fichiers de données"""
    if not TOURNAMENTS_FILE.exists():
        with open(TOURNAMENTS_FILE, 'w') as f:
            json.dump([], f)
    
    if not ARCHETYPES_FILE.exists():
        with open(ARCHETYPES_FILE, 'w') as f:
            json.dump([], f)
    
    if not STATS_FILE.exists():
        with open(STATS_FILE, 'w') as f:
            json.dump({"tournaments": 0, "archetypes": 0, "formats": {}}, f)

# Initialiser les intégrations
integration_service = None

def init_integrations():
    """Initialiser les intégrations réelles"""
    global integration_service
    try:
        # Importer seulement si les dépendances sont disponibles
        from integrations.integration_service import IntegrationService
        
        integration_service = IntegrationService()
        integration_service.create_sample_archetype_data("Modern")
        integration_service.create_sample_archetype_data("Standard")
        
        logger.info("✅ Intégrations réelles initialisées")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ Intégrations non disponibles (dépendances manquantes): {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation des intégrations: {e}")
        return False

# Modèles Pydantic
class Tournament(BaseModel):
    name: str
    date: str
    format: str
    source: str = "manual"
    players: List[str] = Field(default_factory=list)
    winner: Optional[str] = None
    decklist_url: Optional[str] = None

class Archetype(BaseModel):
    name: str
    format: str
    description: str = ""
    key_cards: List[str] = Field(default_factory=list)
    colors: str = ""
    strategy: str = ""

class DeckScrapeRequest(BaseModel):
    url: str
    format: str = "Modern"

class MetaAnalysisRequest(BaseModel):
    format: str = "Modern"
    days: int = 7

# Fonctions utilitaires
def load_json(file_path: Path) -> Any:
    """Charger un fichier JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {file_path}: {e}")
        return [] if file_path.name != "stats.json" else {"tournaments": 0, "archetypes": 0, "formats": {}}

def save_json(file_path: Path, data: Any) -> bool:
    """Sauvegarder un fichier JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de {file_path}: {e}")
        return False

def update_stats():
    """Mettre à jour les statistiques"""
    tournaments = load_json(TOURNAMENTS_FILE)
    archetypes = load_json(ARCHETYPES_FILE)
    
    # Compter les formats
    formats = {}
    for tournament in tournaments:
        fmt = tournament.get("format", "Unknown")
        formats[fmt] = formats.get(fmt, 0) + 1
    
    stats = {
        "tournaments": len(tournaments),
        "archetypes": len(archetypes),
        "formats": formats,
        "last_updated": datetime.now().isoformat()
    }
    
    save_json(STATS_FILE, stats)
    return stats

# Endpoints API existants
@app.get("/health")
async def health_check():
    """Vérification de santé honnête"""
    return {
        "status": "healthy",
        "service": "Metalyzr MVP",
        "version": "2.0.0",
        "integrations": {
            "jiliac_cache": integration_service is not None,
            "mtg_scraper": integration_service is not None,
            "badaro_engine": integration_service is not None
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats")
async def get_stats():
    """Obtenir les statistiques"""
    stats = load_json(STATS_FILE)
    
    # Ajouter les statistiques des intégrations
    if integration_service:
        integration_status = integration_service.get_integration_status()
        stats["integrations"] = integration_status
    
    return stats

@app.get("/api/tournaments")
async def get_tournaments():
    """Obtenir la liste des tournois"""
    tournaments = load_json(TOURNAMENTS_FILE)
    return {"tournaments": tournaments}

@app.post("/api/tournaments")
async def create_tournament(tournament: Tournament):
    """Créer un nouveau tournoi"""
    tournaments = load_json(TOURNAMENTS_FILE)
    
    # Ajouter l'ID et la date de création
    tournament_data = tournament.dict()
    tournament_data["id"] = len(tournaments) + 1
    tournament_data["created_at"] = datetime.now().isoformat()
    
    tournaments.append(tournament_data)
    save_json(TOURNAMENTS_FILE, tournaments)
    update_stats()
    
    logger.info(f"Tournoi créé: {tournament.name}")
    return {"message": "Tournoi créé avec succès", "tournament": tournament_data}

@app.get("/api/archetypes")
async def get_archetypes():
    """Obtenir la liste des archétypes"""
    archetypes = load_json(ARCHETYPES_FILE)
    return {"archetypes": archetypes}

@app.post("/api/archetypes")
async def create_archetype(archetype: Archetype):
    """Créer un nouvel archétype"""
    archetypes = load_json(ARCHETYPES_FILE)
    
    # Ajouter l'ID et la date de création
    archetype_data = archetype.dict()
    archetype_data["id"] = len(archetypes) + 1
    archetype_data["created_at"] = datetime.now().isoformat()
    
    archetypes.append(archetype_data)
    save_json(ARCHETYPES_FILE, archetypes)
    update_stats()
    
    logger.info(f"Archétype créé: {archetype.name}")
    return {"message": "Archétype créé avec succès", "archetype": archetype_data}

# Nouveaux endpoints pour les intégrations réelles
@app.get("/api/integrations/status")
async def get_integrations_status():
    """Obtenir le statut des intégrations"""
    if not integration_service:
        return {"status": "disabled", "message": "Intégrations non disponibles"}
    
    return integration_service.get_integration_status()

@app.get("/api/integrations/tournaments/recent")
async def get_recent_tournaments_with_archetypes(format_name: str = "Modern", days: int = 7):
    """Obtenir les tournois récents avec classification d'archétypes"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    try:
        tournaments = integration_service.get_recent_tournaments_with_archetypes(days, format_name)
        return {
            "tournaments": tournaments,
            "count": len(tournaments),
            "format": format_name,
            "days": days
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tournois: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations/scrape/deck")
async def scrape_and_classify_deck(request: DeckScrapeRequest):
    """Scraper un deck et le classifier"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    try:
        deck_data = integration_service.scrape_and_classify_deck(request.url, request.format)
        if not deck_data:
            raise HTTPException(status_code=400, detail="Impossible de scraper le deck")
        
        return deck_data
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations/scrape/multiple")
async def scrape_multiple_decks(urls: List[str], format_name: str = "Modern"):
    """Scraper plusieurs decks et les classifier"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    try:
        decks = integration_service.scrape_multiple_decks_and_classify(urls, format_name)
        return {
            "decks": decks,
            "count": len(decks),
            "format": format_name
        }
    except Exception as e:
        logger.error(f"Erreur lors du scraping multiple: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations/meta/analysis")
async def get_meta_analysis(request: MetaAnalysisRequest):
    """Obtenir une analyse du méta"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    try:
        analysis = integration_service.get_meta_analysis(request.format, request.days)
        return analysis
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse méta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrations/tournaments/search")
async def search_tournaments_by_archetype(archetype: str, format_name: str = "Modern"):
    """Rechercher des tournois par archétype"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    try:
        tournaments = integration_service.search_tournaments_by_archetype(archetype, format_name)
        return {
            "tournaments": tournaments,
            "count": len(tournaments),
            "archetype": archetype,
            "format": format_name
        }
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrations/supported-sites")
async def get_supported_sites():
    """Obtenir la liste des sites supportés pour le scraping"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    sites = integration_service.mtg_scraper.get_supported_sites()
    return {"supported_sites": sites}

@app.get("/api/integrations/supported-formats")
async def get_supported_formats():
    """Obtenir la liste des formats supportés"""
    if not integration_service:
        raise HTTPException(status_code=503, detail="Intégrations non disponibles")
    
    formats = integration_service.badaro_engine.get_supported_formats()
    return {"supported_formats": formats}

# Événements de démarrage et arrêt
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("🚀 Démarrage Metalyzr MVP - Backend honnête")
    logger.info("📊 API disponible sur http://localhost:8000")
    logger.info("📚 Documentation: http://localhost:8000/docs")
    logger.info("💾 Données: Fichiers JSON locaux")
    
    # Initialiser les fichiers de données
    init_data_files()
    
    # Initialiser les intégrations
    integrations_ok = init_integrations()
    
    if integrations_ok:
        logger.info("✅ Toutes les intégrations sont actives")
        logger.info("🔄 Jiliac Cache: Tournois récents")
        logger.info("🕷️ MTG Scraper: Sites supportés")
        logger.info("🎯 Badaro Engine: Classification d'archétypes")
    else:
        logger.warning("⚠️ Intégrations non disponibles - Mode MVP basique")
        logger.info("📝 Installation requise: pip install -r requirements_integrations.txt")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    logger.info("🛑 Arrêt Metalyzr MVP")
    
    # Fermer les intégrations
    if integration_service:
        integration_service.close()
        logger.info("✅ Intégrations fermées")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 