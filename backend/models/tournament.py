from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Tournament(Base):
    __tablename__ = 'tournaments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    format = Column(String(50), nullable=False)  # Standard, Modern, Legacy, etc.
    date = Column(DateTime, nullable=False)
    location = Column(String(200))
    organizer = Column(String(100))
    
    # Métadonnées du tournoi
    total_players = Column(Integer)
    rounds = Column(Integer)
    tournament_type = Column(String(50))  # Swiss, Single Elimination, etc.
    
    # URLs et sources
    source_url = Column(String(500))
    source_site = Column(String(100))  # mtgtop8, mtggoldfish, etc.
    
    # Statut de scraping
    scraped_at = Column(DateTime)
    is_complete = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    decks = relationship("Deck", back_populates="tournament") 