"""
Client API pour Melee.gg
Récupération de données de tournois en temps réel via API officielle
"""
import logging
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

logger = logging.getLogger(__name__)

# The API endpoint for start.gg's GraphQL API
API_URL = "https://api.start.gg/gql/alpha"

# The videogameId for "Magic: The Gathering" on the start.gg platform.
# This was found by exploring their API.
MTG_VIDEOGAME_ID = 1

class GraphQLClient:
    """
    A client to interact with the start.gg GraphQL API.
    This replaces the previous REST client.
    """
    def __init__(self):
        auth_token = os.getenv("STARTGG_API_TOKEN")
        if not auth_token:
            logger.warning("STARTGG_API_TOKEN environment variable not set. Making anonymous requests.")
            headers = {}
        else:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
        transport = AIOHTTPTransport(url=API_URL, headers=headers)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    async def get_tournaments_by_game(
        self, 
        days_ago: int = 14,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Fetches recent, completed tournaments for a specific videogame.
        """
        after_timestamp = int((datetime.now() - timedelta(days=days_ago)).timestamp())

        query = gql("""
            query TournamentsByVideogame($videogameId: ID!, $after: Timestamp!, $limit: Int!) {
                tournaments(query: {
                    perPage: $limit,
                    filter: {
                        past: false,
                        videogameIds: [$videogameId],
                        afterDate: $after,
                        status: 1 # (1 = completed)
                    }
                }) {
                    nodes {
                        id
                        name
                        slug
                        startAt
                        events {
                            name
                            entrants {
                                nodes {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        """)

        variables = {
            "videogameId": MTG_VIDEOGAME_ID,
            "after": after_timestamp,
            "limit": limit
        }

        try:
            logger.info(f"Fetching last {days_ago} days of MTG tournaments from start.gg API.")
            result = await self.client.execute_async(query, variable_values=variables)
            
            if result and result.get("tournaments") and result["tournaments"].get("nodes"):
                tournaments = result["tournaments"]["nodes"]
                logger.info(f"Successfully fetched {len(tournaments)} tournaments.")
                return tournaments
            else:
                logger.warning("No tournaments found in the API response.")
                return []
        except Exception as e:
            logger.error(f"An error occurred while fetching tournaments from GraphQL API: {e}", exc_info=True)
            return [] 