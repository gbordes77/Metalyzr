from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

# Table d'association pour les règles many-to-many
archetype_rules = Table('archetype_rules', Base.metadata,
    Column('archetype_id', Integer, ForeignKey('archetypes.id')),
    Column('rule_id', Integer, ForeignKey('detection_rules.id'))
)

class Archetype(Base):
    __tablename__ = 'archetypes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    format = Column(String(50), nullable=False)  # Standard, Modern, Legacy, etc.
    category = Column(String(50))  # Aggro, Control, Combo, Midrange, etc.
    description = Column(String(500))
    color_identity = Column(String(10))  # W, U, B, R, G combinations
    key_cards = Column(JSON)  # Liste des cartes essentielles
    variations = Column(JSON)  # Variantes connues
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))  # Admin qui a créé
    
    # Relations
    rules = relationship("DetectionRule", secondary=archetype_rules, back_populates="archetypes")
    decks = relationship("Deck", back_populates="archetype")
    
class DetectionRule(Base):
    __tablename__ = 'detection_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    rule_type = Column(String(50))  # 'contains_all', 'contains_any', 'regex', 'threshold'
    conditions = Column(JSON)  # {"cards": ["Lightning Bolt", "Goblin Guide"], "min_count": 4}
    priority = Column(Integer, default=0)  # Ordre d'application des règles
    confidence_score = Column(Integer, default=100)  # Confiance dans la règle (0-100)
    active = Column(Boolean, default=True)
    
    # Relations
    archetypes = relationship("Archetype", secondary=archetype_rules, back_populates="rules") 