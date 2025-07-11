import logging
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, List, Set

from backend import models
from backend.database import get_db_session

logger = logging.getLogger(__name__)

class DataStorage:
    """
    Handles all database operations for the collectors using SQLAlchemy.
    """

    @contextmanager
    def _session_scope(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        with get_db_session() as db:
            yield db

    def get_or_create(self, db: Session, model, defaults: Dict = None, **kwargs) -> Any:
        instance = db.query(model).filter_by(**kwargs).one_or_none()
        if instance:
            return instance
        else:
            params = {**kwargs, **(defaults or {})}
            instance = model(**params)
            db.add(instance)
            db.flush() # Use flush to get the ID without committing
            return instance

    def save_tournament_data(self, tournament_data: Dict[str, Any]) -> int | None:
        """
        Saves a tournament and all its related data (decks, cards, matches)
        in a single transaction.
        """
        with self._session_scope() as db:
            try:
                # 1. Get or Create Source and Format
                source = self.get_or_create(db, models.Source, source_name=tournament_data['source'])
                t_format = self.get_or_create(db, models.Format, format_name=tournament_data['format'])

                # 2. Create Tournament
                tournament = self.get_or_create(
                    db,
                    models.Tournament,
                    tournament_uuid=tournament_data['uuid'],
                    defaults={
                        'tournament_name': tournament_data['name'],
                        'tournament_date': tournament_data['date'],
                        'source_id': source.source_id,
                        'format_id': t_format.format_id,
                    }
                )
                
                # 3. Process Decks
                if tournament_data.get('decks'):
                    self._process_decks(db, tournament_data['decks'], tournament.tournament_id)
                
                db.commit()
                logger.info(f"Successfully saved tournament '{tournament.tournament_name}' (ID: {tournament.tournament_id})")
                return tournament.tournament_id

            except IntegrityError:
                logger.warning(f"Tournament with UUID {tournament_data.get('uuid')} likely already exists. Rolling back.")
                db.rollback()
                return None
            except Exception as e:
                logger.error(f"Error saving tournament data: {e}", exc_info=True)
                db.rollback()
                raise

    def _process_decks(self, db: Session, decks_data: List[Dict[str, Any]], tournament_id: int):
        """Processes and saves a list of decks for a tournament."""
        all_card_names = set()
        for deck in decks_data:
            all_card_names.update(card['name'] for card in deck.get('mainboard', []))
            all_card_names.update(card['name'] for card in deck.get('sideboard', []))
        
        card_map = self._get_or_create_cards(db, all_card_names)

        for deck_data in decks_data:
            archetype_name = deck_data.get('archetype', 'Unknown')
            archetype = self.get_or_create(db, models.Archetype, archetype_name=archetype_name)
            
            deck_obj = models.Deck(
                tournament_id=tournament_id,
                player_name=deck_data.get('player'),
                archetype_id=archetype.archetype_id,
                decklist_json=deck_data # Store the raw deck data as well
            )
            db.add(deck_obj)
            db.flush() # Flush to get deck_id

            deck_cards = []
            for card_info in deck_data.get('mainboard', []):
                card_id = card_map.get(card_info['name'])
                if card_id:
                    deck_cards.append({'deck_id': deck_obj.deck_id, 'card_id': card_id, 'quantity': card_info['quantity'], 'is_sideboard': False})
            
            for card_info in deck_data.get('sideboard', []):
                card_id = card_map.get(card_info['name'])
                if card_id:
                    deck_cards.append({'deck_id': deck_obj.deck_id, 'card_id': card_id, 'quantity': card_info['quantity'], 'is_sideboard': True})
            
            if deck_cards:
                db.bulk_insert_mappings(models.DeckCard, deck_cards)

    def _get_or_create_cards(self, db: Session, card_names: Set[str]) -> Dict[str, int]:
        """Gets or creates all necessary cards and returns a name-to-ID map."""
        existing_cards = {c.card_name: c.card_id for c in db.query(models.Card).filter(models.Card.card_name.in_(card_names))}
        
        new_cards_to_create = []
        for name in card_names:
            if name not in existing_cards:
                new_cards_to_create.append({'card_name': name})
        
        if new_cards_to_create:
            db.bulk_insert_mappings(models.Card, new_cards_to_create)
            db.flush() # Important to flush to get IDs for the next query
            
            # Re-fetch all cards to get a complete map
            all_cards = {c.card_name: c.card_id for c in db.query(models.Card).filter(models.Card.card_name.in_(card_names))}
            return all_cards

        return existing_cards 