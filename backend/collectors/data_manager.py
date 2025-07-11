import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from config import config

class DataManager:
    """Gestionnaire de données pour sauvegarder les résultats du scraping"""
    
    def __init__(self):
        self.logger = logging.getLogger("scraper.data_manager")
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def save_tournament_data(self, tournament_data: Dict[str, Any]) -> Optional[int]:
        """Sauvegarde les données d'un tournoi et retourne l'ID"""
        session = self.SessionLocal()
        
        try:
            from models import Tournament, Deck, Card
            
            # Vérifier si le tournoi existe déjà
            existing_tournament = session.query(Tournament).filter(
                Tournament.source_url == tournament_data['source_url']
            ).first()
            
            if existing_tournament:
                self.logger.info(f"Tournament already exists: {tournament_data['name']}")
                return existing_tournament.id
            
            # Créer le tournoi
            tournament = Tournament(
                name=tournament_data['name'],
                format=tournament_data['format'],
                date=tournament_data['date'],
                location=tournament_data.get('location', ''),
                organizer=tournament_data.get('organizer', ''),
                total_players=tournament_data.get('total_players', 0),
                rounds=tournament_data.get('rounds', 0),
                tournament_type=tournament_data.get('tournament_type', ''),
                source_url=tournament_data['source_url'],
                source_site=tournament_data['source_site'],
                scraped_at=datetime.now(),
                is_complete=tournament_data.get('is_complete', False)
            )
            
            session.add(tournament)
            session.flush()  # Pour obtenir l'ID
            
            # Sauvegarder les decks
            decks_data = tournament_data.get('decks', [])
            saved_decks = 0
            
            for deck_data in decks_data:
                deck_id = self.save_deck_data(session, deck_data, tournament.id)
                if deck_id:
                    saved_decks += 1
            
            session.commit()
            
            self.logger.info(f"Saved tournament '{tournament.name}' with {saved_decks} decks")
            return tournament.id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving tournament data: {str(e)}")
            return None
        finally:
            session.close()
    
    def save_deck_data(self, session, deck_data: Dict[str, Any], tournament_id: int) -> Optional[int]:
        """Sauvegarde les données d'un deck"""
        try:
            from models import Deck
            
            # Créer le deck
            deck = Deck(
                player_name=deck_data['player_name'],
                position=deck_data.get('position'),
                wins=deck_data.get('wins', 0),
                losses=deck_data.get('losses', 0),
                draws=deck_data.get('draws', 0),
                mainboard=deck_data.get('mainboard', {}),
                sideboard=deck_data.get('sideboard', {}),
                color_identity=deck_data.get('color_identity', ''),
                total_cards=deck_data.get('total_cards', 60),
                tournament_id=tournament_id
            )
            
            session.add(deck)
            session.flush()
            
            # Sauvegarder les cartes si elles n'existent pas
            self.save_cards_from_deck(session, deck_data)
            
            return deck.id
            
        except Exception as e:
            self.logger.error(f"Error saving deck data: {str(e)}")
            return None
    
    def save_cards_from_deck(self, session, deck_data: Dict[str, Any]):
        """Sauvegarde les cartes d'un deck dans la base de données"""
        try:
            from models import Card
            
            # Combiner mainboard et sideboard
            all_cards = {}
            all_cards.update(deck_data.get('mainboard', {}))
            all_cards.update(deck_data.get('sideboard', {}))
            
            for card_name, count in all_cards.items():
                # Vérifier si la carte existe déjà
                existing_card = session.query(Card).filter(Card.name == card_name).first()
                
                if not existing_card:
                    # Créer une nouvelle carte avec des données minimales
                    card = Card(
                        name=card_name,
                        # Les autres champs seront remplis par un autre processus
                        # ou par l'API Scryfall
                    )
                    session.add(card)
                    
        except Exception as e:
            self.logger.error(f"Error saving cards: {str(e)}")
    
    def get_tournament_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des tournois scrapés"""
        session = self.SessionLocal()
        
        try:
            from models import Tournament, Deck
            from sqlalchemy import func
            
            # Statistiques des tournois
            total_tournaments = session.query(Tournament).count()
            total_decks = session.query(Deck).count()
            
            # Tournois par format
            format_stats = session.query(
                Tournament.format,
                func.count(Tournament.id).label('count')
            ).group_by(Tournament.format).all()
            
            # Tournois par site source
            source_stats = session.query(
                Tournament.source_site,
                func.count(Tournament.id).label('count')
            ).group_by(Tournament.source_site).all()
            
            return {
                "total_tournaments": total_tournaments,
                "total_decks": total_decks,
                "formats": {stat.format: stat.count for stat in format_stats},
                "sources": {stat.source_site: stat.count for stat in source_stats}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tournament stats: {str(e)}")
            return {}
        finally:
            session.close()
    
    def cleanup_old_data(self, days_old: int = 30):
        """Nettoie les données anciennes"""
        session = self.SessionLocal()
        
        try:
            from models import Tournament
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            old_tournaments = session.query(Tournament).filter(
                Tournament.scraped_at < cutoff_date
            ).count()
            
            if old_tournaments > 0:
                session.query(Tournament).filter(
                    Tournament.scraped_at < cutoff_date
                ).delete()
                session.commit()
                
                self.logger.info(f"Cleaned up {old_tournaments} old tournaments")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error cleaning up old data: {str(e)}")
        finally:
            session.close() 