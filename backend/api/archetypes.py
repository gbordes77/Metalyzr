from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Archetype, Deck

router = APIRouter(prefix="/api/archetypes", tags=["archetypes"])

@router.get("/")
async def list_archetypes(
    format: Optional[str] = Query(None, description="Filtrer par format"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db)
):
    """Liste tous les archétypes avec statistiques"""
    query = db.query(Archetype)
    
    if format:
        query = query.filter(Archetype.format == format)
    if category:
        query = query.filter(Archetype.category == category)
    
    archetypes = query.all()
    
    result = []
    for archetype in archetypes:
        # Compter les decks de cet archétype
        deck_count = db.query(Deck).filter(Deck.archetype_id == archetype.id).count()
        
        result.append({
            "id": archetype.id,
            "name": archetype.name,
            "format": archetype.format,
            "category": archetype.category,
            "description": archetype.description,
            "color_identity": archetype.color_identity,
            "key_cards": archetype.key_cards,
            "deck_count": deck_count
        })
    
    return result

@router.get("/{archetype_id}")
async def get_archetype(archetype_id: int, db: Session = Depends(get_db)):
    """Récupère un archétype spécifique avec statistiques détaillées"""
    archetype = db.query(Archetype).filter(Archetype.id == archetype_id).first()
    
    if not archetype:
        raise HTTPException(status_code=404, detail="Archétype non trouvé")
    
    # Statistiques des decks
    from sqlalchemy import func
    deck_stats = db.query(
        func.count(Deck.id).label('total_decks'),
        func.avg(Deck.wins).label('avg_wins'),
        func.avg(Deck.losses).label('avg_losses'),
        func.min(Deck.position).label('best_position')
    ).filter(Deck.archetype_id == archetype_id).first()
    
    return {
        "id": archetype.id,
        "name": archetype.name,
        "format": archetype.format,
        "category": archetype.category,
        "description": archetype.description,
        "color_identity": archetype.color_identity,
        "key_cards": archetype.key_cards,
        "variations": archetype.variations,
        "created_at": archetype.created_at.isoformat() if archetype.created_at else None,
        "statistics": {
            "total_decks": deck_stats.total_decks or 0,
            "avg_wins": round(float(deck_stats.avg_wins or 0), 2),
            "avg_losses": round(float(deck_stats.avg_losses or 0), 2),
            "best_position": deck_stats.best_position
        }
    }

@router.get("/{archetype_id}/decks")
async def get_archetype_decks(
    archetype_id: int,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Liste les decks d'un archétype spécifique"""
    archetype = db.query(Archetype).filter(Archetype.id == archetype_id).first()
    
    if not archetype:
        raise HTTPException(status_code=404, detail="Archétype non trouvé")
    
    decks = db.query(Deck).filter(
        Deck.archetype_id == archetype_id
    ).order_by(Deck.position.asc()).limit(limit).all()
    
    return [
        {
            "id": deck.id,
            "player_name": deck.player_name,
            "position": deck.position,
            "wins": deck.wins,
            "losses": deck.losses,
            "tournament_id": deck.tournament_id,
            "tournament_name": deck.tournament.name if deck.tournament else None,
            "color_identity": deck.color_identity,
            "confidence": deck.archetype_confidence
        }
        for deck in decks
    ]

@router.get("/formats")
async def get_formats(db: Session = Depends(get_db)):
    """Liste tous les formats disponibles"""
    from sqlalchemy import distinct
    
    formats = db.query(distinct(Archetype.format)).all()
    return [f[0] for f in formats if f[0]]

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Liste toutes les catégories d'archétypes"""
    from sqlalchemy import distinct
    
    categories = db.query(distinct(Archetype.category)).all()
    return [c[0] for c in categories if c[0]] 