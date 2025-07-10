"""
Service to manage the Metagame data pipeline.
- Scrapes tournament data using an external scraper.
- Classifies decks using the Badaro Archetype Engine.
- Loads the data into the database.
"""
import logging
import asyncio
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Integrations
from integrations.startgg_client import StartGGClient
# Removed MTGGoldfish scraper
from integrations.badaro_archetype_engine import BadaroArchetypeEngine
from database import DatabaseClient

logger = logging.getLogger(__name__)

class MetagameService:
    """Service to manage the metagame data pipeline using Melee.gg API."""
    
    def __init__(self, database_client: DatabaseClient, task_status_dict: Dict[str, Any]):
        self.db_client = database_client
        self.startgg_client = StartGGClient()
        self.archetype_engine = BadaroArchetypeEngine()
        self.task_status = task_status_dict

    def _update_status(self, progress: int, total: int, message: str):
        self.task_status.update({
            "progress": progress,
            "total": total,
            "message": message,
        })
        logger.info(f"[Status Update] {message} ({progress}/{total})")

    async def update_metagame_data(self, format_name: Optional[str] = "standard", start_date: Optional[date] = None):
        try:
            self.task_status.update({"status": "running", "error": None})
            days_to_fetch = (datetime.now().date() - start_date).days if start_date else 7
            
            # --- Step 1: Fetch from start.gg ---
            self._update_status(0, 1, "Fetching tournaments from start.gg...")
            startgg_tournaments = await self.startgg_client.get_tournaments_by_game(days_ago=days_to_fetch)
            logger.info(f"Found {len(startgg_tournaments)} tournaments on start.gg.")

            all_tournaments = startgg_tournaments
            
            if not all_tournaments:
                self._update_status(1, 1, "No new tournaments found from any source.")
                self.task_status.update({"status": "completed"})
                return

            # --- Step 2: Process all tournaments ---
            total_tournaments = len(all_tournaments)
            self._update_status(0, total_tournaments, f"Processing {total_tournaments} found tournaments...")
            
            processed_count = 0
            for tournament_data in all_tournaments:
                await self.db_client.save_tournament(tournament_data)
                processed_count += 1
                self._update_status(processed_count, total_tournaments, f"Saved tournament {processed_count}/{total_tournaments}: {tournament_data.get('name')}")

            self.task_status.update({"status": "completed"})
            logger.info("Metagame data update process completed successfully.")

        except Exception as e:
            logger.error(f"Error updating metagame data: {e}", exc_info=True)
            self.task_status.update({"status": "failed", "error": str(e)})

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