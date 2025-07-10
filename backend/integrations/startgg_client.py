import os
import logging
from typing import Optional, List, Dict, Any
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class StartGGClient:
    def __init__(self):
        api_key = os.getenv("STARTGG_API_KEY")
        if not api_key:
            raise ValueError("STARTGG_API_KEY not found in environment variables.")
        
        self.url = "https://api.start.gg/gql/alpha"
        headers = {"Authorization": f"Bearer {api_key}"}
        self.transport = AIOHTTPTransport(url=self.url, headers=headers)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

    async def get_tournaments_by_game(self, days_ago: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        query = gql(
            """
            query TournamentsByVideogame($perPage: Int!, $videogameId: ID!) {
              tournaments(query: {
                perPage: $perPage
                page: 1
                sortBy: "startAt desc"
                filter: {
                  videogameIds: [$videogameId]
                  # We will filter for Magic tournaments after the initial fetch
                }
              }) {
                nodes {
                  id
                  name
                  slug
                  startAt
                  events {
                      id
                      name
                      videogame {
                          id
                          name
                      }
                  }
                }
              }
            }
            """
        )
        variables = {"perPage": limit, "videogameId": 1386} # 1386 is Magic: The Gathering
        
        try:
            async with self.client as session:
                result = await session.execute(query, variable_values=variables)
            
            if not result or not result.get("tournaments", {}).get("nodes"):
                logger.warning("No tournaments found in start.gg response.")
                return []

            all_tournaments = result["tournaments"]["nodes"]
            magic_tournaments = []

            for tournament in all_tournaments:
                # Post-fetch filtering: check if any event is actually a Magic event
                is_magic_tournament = False
                if tournament.get("events"):
                    for event in tournament["events"]:
                        if event.get("videogame", {}).get("name") == "Magic: The Gathering":
                            is_magic_tournament = True
                            break
                if is_magic_tournament:
                    magic_tournaments.append(tournament)

            logger.info(f"Successfully fetched {len(all_tournaments)} total tournaments, filtered down to {len(magic_tournaments)} Magic: The Gathering tournaments.")
            return magic_tournaments

        except Exception as e:
            logger.error(f"Error fetching data from start.gg API: {e}", exc_info=True)
            return [] 