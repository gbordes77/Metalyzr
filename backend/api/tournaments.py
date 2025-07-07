from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Tournament, Deck

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])

@router.get("/", response_model=List[dict])
async def list_tournaments(
    format: Optional[str] = Query(None, description="Filtrer par format"),
    limit: int = Query(50, le=100, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour pagination"),
    db: Session = Depends(get_db)
):
    """Liste les tournois avec pagination et filtres"""
    query = db.query(Tournament)
    
    if format:
        query = query.filter(Tournament.format == format)
    
    tournaments = query.order_by(Tournament.date.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "format": t.format,
            "date": t.date.isoformat(),
            "location": t.location,
            "total_players": t.total_players,
            "rounds": t.rounds,
            "is_complete": t.is_complete
        }
        for t in tournaments
    ]

@router.get("/{tournament_id}")
async def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    """Récupère un tournoi spécifique avec ses decks"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    
    # Compter les decks par archétype
    decks_count = db.query(Deck).filter(Deck.tournament_id == tournament_id).count()
    
    return {
        "id": tournament.id,
        "name": tournament.name,
        "format": tournament.format,
        "date": tournament.date.isoformat(),
        "location": tournament.location,
        "organizer": tournament.organizer,
        "total_players": tournament.total_players,
        "rounds": tournament.rounds,
        "tournament_type": tournament.tournament_type,
        "source_site": tournament.source_site,
        "is_complete": tournament.is_complete,
        "decks_count": decks_count,
        "created_at": tournament.created_at.isoformat() if tournament.created_at else None
    }

@router.get("/{tournament_id}/metagame")
async def get_tournament_metagame(tournament_id: int, db: Session = Depends(get_db)):
    """Analyse du métagame d'un tournoi spécifique"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    
    # Agrégation des archétypes
    from sqlalchemy import func
    from models import Archetype
    
    metagame = db.query(
        Archetype.name,
        Archetype.category,
        func.count(Deck.id).label('deck_count'),
        func.avg(Deck.wins).label('avg_wins'),
        func.max(Deck.position).label('best_position')
    ).join(
        Deck, Deck.archetype_id == Archetype.id
    ).filter(
        Deck.tournament_id == tournament_id
    ).group_by(
        Archetype.id, Archetype.name, Archetype.category
    ).order_by(
        func.count(Deck.id).desc()
    ).all()
    
    total_decks = sum(row.deck_count for row in metagame)
    
    return {
        "tournament_id": tournament_id,
        "tournament_name": tournament.name,
        "total_decks": total_decks,
        "metagame": [
            {
                "archetype": row.name,
                "category": row.category,
                "deck_count": row.deck_count,
                "meta_share": round((row.deck_count / total_decks * 100), 2) if total_decks > 0 else 0,
                "avg_wins": round(float(row.avg_wins or 0), 2),
                "best_position": row.best_position
            }
            for row in metagame
        ]
    }

@router.get("/{tournament_id}/decks")
async def get_tournament_decks(
    tournament_id: int,
    archetype: Optional[str] = Query(None, description="Filtrer par archétype"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Liste les decks d'un tournoi"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournoi non trouvé")
    
    query = db.query(Deck).filter(Deck.tournament_id == tournament_id)
    
    if archetype:
        from models import Archetype
        query = query.join(Archetype).filter(Archetype.name == archetype)
    
    decks = query.order_by(Deck.position.asc()).limit(limit).all()
    
    return [
        {
            "id": deck.id,
            "player_name": deck.player_name,
            "position": deck.position,
            "wins": deck.wins,
            "losses": deck.losses,
            "draws": deck.draws,
            "archetype": deck.archetype.name if deck.archetype else "Unknown",
            "color_identity": deck.color_identity,
            "total_cards": deck.total_cards
        }
        for deck in decks
    ] 