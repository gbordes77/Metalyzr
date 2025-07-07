from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON
from datetime import datetime
from .base import Base

class Card(Base):
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    mana_cost = Column(String(50))  # {3}{R}{R}
    cmc = Column(Integer)  # Converted mana cost
    type_line = Column(String(100))  # Creature — Goblin Warrior
    
    # Caractéristiques
    colors = Column(String(10))  # WUBRG
    color_identity = Column(String(10))  # WUBRG pour commander
    power = Column(String(10))  # Peut être *, X, etc.
    toughness = Column(String(10))
    
    # Métadonnées
    set_code = Column(String(10))
    rarity = Column(String(20))  # common, uncommon, rare, mythic
    oracle_text = Column(Text)
    
    # Données de popularité
    play_rate = Column(Float)  # % d'apparition dans les decks
    win_rate = Column(Float)  # % de victoire quand jouée
    meta_share = Column(Float)  # % du métagame
    
    # Métadonnées de scraping
    scryfall_id = Column(String(50), unique=True)
    gatherer_id = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 