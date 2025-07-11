"""
Modèles de données pour le scraper
Importe les modèles depuis le backend
"""

import sys
import os

# Ajouter le chemin vers le backend
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Importer tous les modèles depuis le backend
try:
    from models.base import Base
    from models.tournament import Tournament
    from models.deck import Deck
    from models.card import Card
    from models.archetype import Archetype, DetectionRule
    
    __all__ = [
        'Base',
        'Tournament',
        'Deck', 
        'Card',
        'Archetype',
        'DetectionRule'
    ]
    
except ImportError as e:
    # Fallback si les modèles ne sont pas accessibles
    print(f"Warning: Could not import models from backend: {e}")
    
    # Définir des modèles minimaux pour éviter les erreurs
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Float, Text
    
    Base = declarative_base()
    
    class Tournament(Base):
        __tablename__ = 'tournaments'
        id = Column(Integer, primary_key=True)
        name = Column(String(200))
        format = Column(String(50))
        date = Column(DateTime)
        location = Column(String(200))
        organizer = Column(String(100))
        total_players = Column(Integer)
        rounds = Column(Integer)
        tournament_type = Column(String(50))
        source_url = Column(String(500))
        source_site = Column(String(100))
        scraped_at = Column(DateTime)
        is_complete = Column(Boolean)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
    
    class Deck(Base):
        __tablename__ = 'decks'
        id = Column(Integer, primary_key=True)
        player_name = Column(String(100))
        position = Column(Integer)
        wins = Column(Integer)
        losses = Column(Integer)
        draws = Column(Integer)
        mainboard = Column(JSON)
        sideboard = Column(JSON)
        archetype_id = Column(Integer, ForeignKey('archetypes.id'))
        color_identity = Column(String(10))
        total_cards = Column(Integer)
        tournament_id = Column(Integer, ForeignKey('tournaments.id'))
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
    
    class Card(Base):
        __tablename__ = 'cards'
        id = Column(Integer, primary_key=True)
        name = Column(String(200))
        mana_cost = Column(String(50))
        cmc = Column(Integer)
        type_line = Column(String(100))
        colors = Column(String(10))
        color_identity = Column(String(10))
        power = Column(String(10))
        toughness = Column(String(10))
        set_code = Column(String(10))
        rarity = Column(String(20))
        oracle_text = Column(Text)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
    
    class Archetype(Base):
        __tablename__ = 'archetypes'
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        format = Column(String(50))
        category = Column(String(50))
        description = Column(String(500))
        color_identity = Column(String(10))
        key_cards = Column(JSON)
        created_at = Column(DateTime)
        updated_at = Column(DateTime)
    
    class DetectionRule(Base):
        __tablename__ = 'detection_rules'
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
        rule_type = Column(String(50))
        conditions = Column(JSON)
        priority = Column(Integer)
        confidence_score = Column(Integer)
        active = Column(Boolean) 