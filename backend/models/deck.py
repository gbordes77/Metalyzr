from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Deck(Base):
    __tablename__ = 'decks'
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String(100), nullable=False)
    position = Column(Integer)  # Classement final
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    
    # Composition du deck
    mainboard = Column(JSON, nullable=False)  # {"Card Name": count, ...}
    sideboard = Column(JSON)  # {"Card Name": count, ...}
    
    # Classification
    archetype_id = Column(Integer, ForeignKey('archetypes.id'))
    archetype_confidence = Column(Float)  # Score de confiance 0-1
    manual_archetype = Column(Boolean, default=False)  # Archetype assigné manuellement
    
    # Couleurs et coût
    color_identity = Column(String(10))  # WUBRG
    mana_curve = Column(JSON)  # {0: count, 1: count, ...}
    total_cards = Column(Integer, default=60)
    
    # Relations tournoi
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    tournament = relationship("Tournament", back_populates="decks")
    archetype = relationship("Archetype") 