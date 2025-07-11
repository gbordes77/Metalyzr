from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
    Float,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class Source(Base):
    __tablename__ = 'sources'
    source_id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(255), unique=True, nullable=False)

class Format(Base):
    __tablename__ = 'formats'
    format_id = Column(Integer, primary_key=True, autoincrement=True)
    format_name = Column(String(255), unique=True, nullable=False)

class Archetype(Base):
    __tablename__ = 'archetypes'
    archetype_id = Column(Integer, primary_key=True, autoincrement=True)
    archetype_name = Column(String(255), unique=True, nullable=False)
    defined_by_user = Column(Boolean, default=False)

class Tournament(Base):
    __tablename__ = 'tournaments'
    tournament_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_uuid = Column(String(255), unique=True, nullable=False)
    tournament_name = Column(String, nullable=False)
    tournament_date = Column(DateTime(timezone=True), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey('sources.source_id'))
    format_id = Column(Integer, ForeignKey('formats.format_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source = relationship("Source")
    format = relationship("Format")

class Deck(Base):
    __tablename__ = 'decks'
    deck_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    player_name = Column(String(255))
    archetype_id = Column(Integer, ForeignKey('archetypes.archetype_id'), index=True)
    classified_archetype_name = Column(String(255))
    base_archetype_name = Column(String(255))
    archetype_confidence = Column(Float)
    decklist_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tournament = relationship("Tournament")
    archetype = relationship("Archetype")

class Card(Base):
    __tablename__ = 'cards'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    card_name = Column(String(255), unique=True, nullable=False)

class DeckCard(Base):
    __tablename__ = 'deck_cards'
    deck_id = Column(Integer, ForeignKey('decks.deck_id'), primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.card_id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    is_sideboard = Column(Boolean, nullable=False, primary_key=True)

class Match(Base):
    __tablename__ = 'matches'
    match_id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
    round_number = Column(Integer)
    deck1_id = Column(Integer, ForeignKey('decks.deck_id'))
    deck2_id = Column(Integer, ForeignKey('decks.deck_id'))
    winner_deck_id = Column(Integer, ForeignKey('decks.deck_id'))
    is_draw = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 