"""
Service to manage the Metagame data pipeline.
- Scrapes tournament data using an external scraper.
- Classifies decks using the Badaro Archetype Engine.
- Loads the data into the database.
"""
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Integrations
from integrations.badaro_archetype_engine import BadaroArchetypeEngine
from integrations.melee_client import MeleeAPIClient
from database import DatabaseClient

logger = logging.getLogger(__name__)

class MetagameService:
    """Service to manage the metagame data pipeline using Melee.gg API."""
    
    def __init__(self, database_client: DatabaseClient, cache_dir: str = "cache/metagame_service"):
        self.db_client = database_client
        self.badaro_engine = BadaroArchetypeEngine(cache_dir)
        # Melee client does not need to be a class member if used in one method
        logger.info("MetagameService initialized for Melee.gg integration.")

    async def update_metagame_data(self, formats: List[str] = ["Modern"], days: int = 7) -> Dict[str, Any]:
        """
        Main ETL method. Fetches recent tournaments from Melee.gg, classifies them,
        and updates the database.
        """
        logger.info(f"Starting metagame update for formats {formats} for the last {days} days.")
        
        async with MeleeAPIClient() as melee_client:
            tasks = [self._process_format(melee_client, f, days) for f in formats]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_tournaments = sum(r for r in results if isinstance(r, int))
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.error(f"Encountered {len(errors)} errors during update: {errors}")

        return {
            "status": "success" if not errors else "partial_success",
            "processed_tournaments": processed_tournaments,
            "errors": len(errors)
        }
        
    async def _process_format(self, client: MeleeAPIClient, format_name: str, days: int) -> int:
        """Fetch and process all tournaments for a given format."""
        logger.info(f"Processing format: {format_name}")
        tournaments = await client.get_tournaments(format_name=format_name, limit=50)
        
        processed_count = 0
        for tourney_summary in tournaments:
            tournament_id = tourney_summary.get("id")
            if not tournament_id:
                continue
            
            # Check if tournament already processed to avoid re-fetching details
            if self.db_client.execute_query("SELECT 1 FROM tournaments WHERE tournament_uuid = %s", (tournament_id,), fetch="one"):
                logger.info(f"Skipping already processed tournament: {tourney_summary.get('name')}")
                continue

            tournament_details = await client.get_tournament_details(tournament_id)
            if not tournament_details:
                continue
                
            classified_decks = []
            for deck in tournament_details.get("decks", []):
                deck_for_classification = {
                    "mainboard": deck.get("mainboard", {}),
                    "sideboard": deck.get("sideboard", {}),
                }
                classification = self.badaro_engine.classify_deck(deck_for_classification, format_name)
                deck["archetype_classification"] = classification
                classified_decks.append(deck)
            tournament_details["decks"] = classified_decks
            
            self._load_tournament_to_db(tournament_details)
            processed_count += 1
            await asyncio.sleep(1)
            
        return processed_count

    def _load_tournament_to_db(self, tournament_data: Dict[str, Any]):
        """
        Loads a single tournament's data from Melee.gg into the database, 
        including its decks, cards, and matches. This is a single, robust transaction.
        """
        with self.db_client.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Upsert format and source, and get their IDs
                    format_name = tournament_data.get("format", "Unknown")
                    cursor.execute("INSERT INTO formats (format_name) VALUES (%s) ON CONFLICT (format_name) DO NOTHING;", (format_name,))
                    cursor.execute("SELECT format_id FROM formats WHERE format_name = %s;", (format_name,))
                    format_id = cursor.fetchone()[0]

                    source_name = tournament_data.get("source_site", "melee.gg")
                    cursor.execute("INSERT INTO sources (source_name) VALUES (%s) ON CONFLICT (source_name) DO NOTHING;", (source_name,))
                    cursor.execute("SELECT source_id FROM sources WHERE source_name = %s;", (source_name,))
                    source_id = cursor.fetchone()[0]

                    # Insert tournament and get its database ID
                    cursor.execute(
                        """
                        INSERT INTO tournaments (tournament_uuid, tournament_name, tournament_date, source_id, format_id)
                        VALUES (%s, %s, %s, %s, %s) RETURNING tournament_id;
                        """,
                        (tournament_data.get("id"), tournament_data.get("name"), tournament_data.get("date"), source_id, format_id)
                    )
                    tournament_id = cursor.fetchone()[0]

                    # Batch-insert all unique cards from the tournament
                    all_cards = set()
                    for deck in tournament_data.get("decks", []):
                        all_cards.update(deck.get("mainboard", {}).keys())
                        all_cards.update(deck.get("sideboard", {}).keys())
                    
                    if all_cards:
                        card_tuples = [(card,) for card in all_cards if card]
                        cursor.executemany("INSERT INTO cards (card_name) VALUES (%s) ON CONFLICT (card_name) DO NOTHING;", card_tuples)
                    
                    cursor.execute("SELECT card_name, card_id FROM cards WHERE card_name = ANY(%s);", (list(all_cards),))
                    card_map = {name: id for name, id in cursor.fetchall()}

                    # Insert decks and matches
                    temp_id_to_deck_id = {}
                    for deck in tournament_data.get("decks", []):
                        archetype_name = deck.get("archetype_classification", {}).get("archetype", "Unknown")
                        cursor.execute("INSERT INTO archetypes (archetype_name) VALUES (%s) ON CONFLICT (archetype_name) DO NOTHING;", (archetype_name,))
                        cursor.execute("SELECT archetype_id FROM archetypes WHERE archetype_name = %s;", (archetype_name,))
                        archetype_id = cursor.fetchone()[0]

                        cursor.execute(
                            """
                            INSERT INTO decks (tournament_id, player_name, archetype_id, classified_archetype_name, base_archetype_name, archetype_confidence, decklist_json)
                            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING deck_id;
                            """,
                            (tournament_id, deck.get("player_name"), archetype_id, archetype_name, 
                            deck.get("archetype_classification", {}).get("base_archetype"),
                            deck.get("archetype_classification", {}).get("confidence"), json.dumps(deck))
                        )
                        deck_id = cursor.fetchone()[0]
                        temp_id_to_deck_id[deck.get("position")] = deck_id # Using position as temp ID from Melee

                        deck_cards_to_insert = []
                        for card_name, count in deck.get("mainboard", {}).items():
                            if card_id := card_map.get(card_name):
                                deck_cards_to_insert.append((deck_id, card_id, count, False))
                        for card_name, count in deck.get("sideboard", {}).items():
                            if card_id := card_map.get(card_name):
                                deck_cards_to_insert.append((deck_id, card_id, count, True))
                        
                        if deck_cards_to_insert:
                            cursor.executemany("INSERT INTO deck_cards (deck_id, card_id, quantity, is_sideboard) VALUES (%s, %s, %s, %s);", deck_cards_to_insert)

                    # Finally, insert the matches using the newly created deck IDs
                    for match in tournament_data.get("matches", []):
                        deck1_db_id = temp_id_to_deck_id.get(match.get("deck1_id"))
                        deck2_db_id = temp_id_to_deck_id.get(match.get("deck2_id"))
                        winner_db_id = temp_id_to_deck_id.get(match.get("winner_deck_id"))
                        
                        if deck1_db_id and deck2_db_id:
                            cursor.execute(
                                "INSERT INTO matches (tournament_id, deck1_id, deck2_id, winner_deck_id, round_name) VALUES (%s, %s, %s, %s, %s);",
                                (tournament_id, deck1_db_id, deck2_db_id, winner_db_id, match.get("round"))
                            )
                    
                    conn.commit()
                    logger.info(f"Successfully loaded Melee tournament '{tournament_data.get('name')}' with {len(tournament_data.get('decks',[]))} decks and {len(tournament_data.get('matches',[]))} matches.")

                except Exception as e:
                    logger.error(f"Error loading tournament to DB for '{tournament_data.get('name')}'. Rolling back. Error: {e}", exc_info=True)
                    conn.rollback()

    def get_service_status(self) -> Dict[str, Any]:
        return {"status": "active", "source": "Melee.gg"}
        
    def close(self):
        logger.info("MetagameService is shutting down.") 