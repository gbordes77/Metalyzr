from sqlalchemy.orm import Session
from . import models, schemas

def get_tournament_by_uuid(db: Session, uuid: str):
    """
    Retrieves a single tournament by its unique UUID.
    """
    return db.query(models.Tournament).filter(models.Tournament.uuid == uuid).first()

def get_tournaments(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of tournaments with pagination.
    """
    return db.query(models.Tournament).order_by(models.Tournament.date.desc()).offset(skip).limit(limit).all()

def create_tournament(db: Session, tournament: schemas.TournamentCreate):
    """
    Creates a new tournament in the database.
    If a tournament with the same UUID already exists, it returns the existing one.
    """
    db_tournament = get_tournament_by_uuid(db, uuid=tournament.uuid)
    if db_tournament:
        return db_tournament
        
    # Create a new tournament instance from the Pydantic schema
    db_tournament = models.Tournament(**tournament.model_dump())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament 