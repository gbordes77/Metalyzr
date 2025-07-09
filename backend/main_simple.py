"""
Backend FastAPI simple et honnête pour Metalyzr MVP
CRUD basique pour tournois et archétypes avec stockage JSON local
Pas de fake APIs, pas de cache fake - seulement ce qui fonctionne vraiment
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuration du logging simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metalyzr")

# Models Pydantic pour validation
class Tournament(BaseModel):
    name: str
    format: str = "Standard"
    date: str
    participants: int
    organizer: str = "Manual Entry"
    description: str = ""

class Archetype(BaseModel):
    name: str
    description: str
    format: str = "Standard"
    colors: str = ""

class TournamentResponse(Tournament):
    id: int

class ArchetypeResponse(Archetype):
    id: int
    tournament_count: int = 0

# FastAPI app simple
app = FastAPI(
    title="Metalyzr MVP", 
    version="1.0.0",
    description="🎯 MVP simple pour gestion de tournois MTG - Données locales uniquement",
    docs_url="/docs"
)

# CORS simple
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Stockage simple JSON local
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
TOURNAMENTS_FILE = DATA_DIR / "tournaments.json"
ARCHETYPES_FILE = DATA_DIR / "archetypes.json"

class DataStore:
    """Gestionnaire de données JSON simple"""
    
    def __init__(self):
        self.tournaments = self._load_tournaments()
        self.archetypes = self._load_archetypes()
    
    def _load_tournaments(self) -> List[Dict]:
        """Charger les tournois depuis le fichier JSON"""
        if TOURNAMENTS_FILE.exists():
            try:
                with open(TOURNAMENTS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement tournois: {e}")
        return []
    
    def _load_archetypes(self) -> List[Dict]:
        """Charger les archétypes depuis le fichier JSON"""
        if ARCHETYPES_FILE.exists():
            try:
                with open(ARCHETYPES_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement archétypes: {e}")
        return []
    
    def _save_tournaments(self):
        """Sauvegarder les tournois dans le fichier JSON"""
        try:
            with open(TOURNAMENTS_FILE, 'w') as f:
                json.dump(self.tournaments, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde tournois: {e}")
    
    def _save_archetypes(self):
        """Sauvegarder les archétypes dans le fichier JSON"""
        try:
            with open(ARCHETYPES_FILE, 'w') as f:
                json.dump(self.archetypes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde archétypes: {e}")
    
    def add_tournament(self, tournament: Tournament) -> Dict:
        """Ajouter un nouveau tournoi"""
        new_id = max([t.get("id", 0) for t in self.tournaments], default=0) + 1
        tournament_data = {
            "id": new_id,
            **tournament.dict(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.tournaments.append(tournament_data)
        self._save_tournaments()
        logger.info(f"Tournoi ajouté: {tournament.name}")
        return tournament_data
    
    def get_tournaments(self, format_filter: Optional[str] = None) -> List[Dict]:
        """Récupérer les tournois avec filtre optionnel"""
        tournaments = self.tournaments.copy()
        if format_filter:
            tournaments = [t for t in tournaments if t.get("format", "").lower() == format_filter.lower()]
        return sorted(tournaments, key=lambda x: x.get("date", ""), reverse=True)
    
    def get_tournament_by_id(self, tournament_id: int) -> Optional[Dict]:
        """Récupérer un tournoi par ID"""
        for tournament in self.tournaments:
            if tournament.get("id") == tournament_id:
                return tournament
        return None
    
    def update_tournament(self, tournament_id: int, tournament: Tournament) -> Optional[Dict]:
        """Mettre à jour un tournoi"""
        for i, t in enumerate(self.tournaments):
            if t.get("id") == tournament_id:
                self.tournaments[i] = {
                    **t,
                    **tournament.dict(),
                    "updated_at": datetime.now().isoformat()
                }
                self._save_tournaments()
                logger.info(f"Tournoi mis à jour: {tournament.name}")
                return self.tournaments[i]
        return None
    
    def delete_tournament(self, tournament_id: int) -> bool:
        """Supprimer un tournoi"""
        for i, t in enumerate(self.tournaments):
            if t.get("id") == tournament_id:
                deleted = self.tournaments.pop(i)
                self._save_tournaments()
                logger.info(f"Tournoi supprimé: {deleted.get('name')}")
                return True
        return False
    
    def add_archetype(self, archetype: Archetype) -> Dict:
        """Ajouter un nouvel archétype"""
        new_id = max([a.get("id", 0) for a in self.archetypes], default=0) + 1
        archetype_data = {
            "id": new_id,
            **archetype.dict(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.archetypes.append(archetype_data)
        self._save_archetypes()
        logger.info(f"Archétype ajouté: {archetype.name}")
        return archetype_data
    
    def get_archetypes(self, format_filter: Optional[str] = None) -> List[Dict]:
        """Récupérer les archétypes avec stats calculées"""
        archetypes = self.archetypes.copy()
        if format_filter:
            archetypes = [a for a in archetypes if a.get("format", "").lower() == format_filter.lower()]
        
        # Calculer le nombre de tournois pour chaque archétype
        for archetype in archetypes:
            archetype["tournament_count"] = sum(
                1 for t in self.tournaments 
                if archetype["name"].lower() in t.get("description", "").lower()
            )
        
        return sorted(archetypes, key=lambda x: x.get("name", ""))
    
    def get_archetype_by_id(self, archetype_id: int) -> Optional[Dict]:
        """Récupérer un archétype par ID"""
        for archetype in self.archetypes:
            if archetype.get("id") == archetype_id:
                return archetype
        return None
    
    def update_archetype(self, archetype_id: int, archetype: Archetype) -> Optional[Dict]:
        """Mettre à jour un archétype"""
        for i, a in enumerate(self.archetypes):
            if a.get("id") == archetype_id:
                self.archetypes[i] = {
                    **a,
                    **archetype.dict(),
                    "updated_at": datetime.now().isoformat()
                }
                self._save_archetypes()
                logger.info(f"Archétype mis à jour: {archetype.name}")
                return self.archetypes[i]
        return None
    
    def delete_archetype(self, archetype_id: int) -> bool:
        """Supprimer un archétype"""
        for i, a in enumerate(self.archetypes):
            if a.get("id") == archetype_id:
                deleted = self.archetypes.pop(i)
                self._save_archetypes()
                logger.info(f"Archétype supprimé: {deleted.get('name')}")
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Calculer les statistiques globales"""
        formats = {}
        for tournament in self.tournaments:
            fmt = tournament.get("format", "Unknown")
            formats[fmt] = formats.get(fmt, 0) + 1
        
        return {
            "tournaments": len(self.tournaments),
            "archetypes": len(self.archetypes),
            "formats": formats,
            "last_update": datetime.now().isoformat()
        }

# Instance globale du store
data_store = DataStore()

# Routes API simples et honnêtes

@app.get("/health")
async def health_check():
    """Health check simple"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Metalyzr MVP fonctionne",
        "data_source": "local_json"
    }

@app.get("/api/stats")
async def get_stats():
    """Statistiques globales"""
    return data_store.get_stats()

# Routes Tournois
@app.get("/api/tournaments", response_model=List[TournamentResponse])
async def get_tournaments(format: Optional[str] = None):
    """Liste des tournois avec filtre optionnel par format"""
    return data_store.get_tournaments(format_filter=format)

@app.get("/api/tournaments/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: int):
    """Détails d'un tournoi spécifique"""
    tournament = data_store.get_tournament_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    return tournament

@app.post("/api/tournaments", response_model=TournamentResponse)
async def create_tournament(tournament: Tournament):
    """Créer un nouveau tournoi"""
    return data_store.add_tournament(tournament)

@app.put("/api/tournaments/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(tournament_id: int, tournament: Tournament):
    """Mettre à jour un tournoi"""
    updated = data_store.update_tournament(tournament_id, tournament)
    if not updated:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    return updated

@app.delete("/api/tournaments/{tournament_id}")
async def delete_tournament(tournament_id: int):
    """Supprimer un tournoi"""
    if not data_store.delete_tournament(tournament_id):
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    return {"message": "Tournoi supprimé avec succès"}

# Routes Archétypes
@app.get("/api/archetypes", response_model=List[ArchetypeResponse])
async def get_archetypes(format: Optional[str] = None):
    """Liste des archétypes avec filtre optionnel par format"""
    return data_store.get_archetypes(format_filter=format)

@app.get("/api/archetypes/{archetype_id}", response_model=ArchetypeResponse)
async def get_archetype(archetype_id: int):
    """Détails d'un archétype spécifique"""
    archetype = data_store.get_archetype_by_id(archetype_id)
    if not archetype:
        raise HTTPException(status_code=404, detail="Archétype non trouvé")
    return archetype

@app.post("/api/archetypes", response_model=ArchetypeResponse)
async def create_archetype(archetype: Archetype):
    """Créer un nouvel archétype"""
    return data_store.add_archetype(archetype)

@app.put("/api/archetypes/{archetype_id}", response_model=ArchetypeResponse)
async def update_archetype(archetype_id: int, archetype: Archetype):
    """Mettre à jour un archétype"""
    updated = data_store.update_archetype(archetype_id, archetype)
    if not updated:
        raise HTTPException(status_code=404, detail="Archétype non trouvé")
    return updated

@app.delete("/api/archetypes/{archetype_id}")
async def delete_archetype(archetype_id: int):
    """Supprimer un archétype"""
    if not data_store.delete_archetype(archetype_id):
        raise HTTPException(status_code=404, detail="Archétype non trouvé")
    return {"message": "Archétype supprimé avec succès"}

@app.get("/")
async def root():
    """Page d'accueil API"""
    return {
        "message": "Metalyzr MVP - Backend honnête et simple",
        "version": "1.0.0", 
        "status": "running",
        "data_source": "local_json",
        "features": [
            "CRUD Tournois",
            "CRUD Archétypes", 
            "Stockage JSON local",
            "API REST complète",
            "Documentation Swagger"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "stats": "/api/stats", 
            "tournaments": "/api/tournaments",
            "archetypes": "/api/archetypes"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Démarrage Metalyzr MVP - Backend honnête")
    logger.info("📊 API disponible sur http://localhost:8000")
    logger.info("📚 Documentation: http://localhost:8000/docs")
    logger.info("💾 Données: Fichiers JSON locaux")
    
    uvicorn.run(
        "main_simple:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 