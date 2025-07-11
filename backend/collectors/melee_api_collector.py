import aiohttp
from typing import List, Dict, Any, Optional

from ..schemas import Tournament
from .utils import parse_date, normalize_format

MELEE_API_URL = "https://melee.gg/api/tournaments"

async def fetch_tournaments_from_api(
    format_name: str = "Modern", limit: int = 20
) -> List[Tournament]:
    """
    Fetches tournament data directly from the official Melee.gg API.
    """
    print(f"Fetching data from Melee.gg API for '{format_name}' format...")
    
    params = {
        "game": "magic",
        "format": format_name,
        "limit": limit,
        "status": "completed"
    }
    
    headers = {
        "User-Agent": "Metalyzr/1.0 (Python/3.11; aiohttp) Official-API-Probe",
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(MELEE_API_URL, params=params, headers=headers) as response:
                response.raise_for_status() # Raises an exception for 4xx/5xx errors
                data = await response.json()
                
                tournaments_data = data if isinstance(data, list) else data.get("tournaments", [])

                processed_tournaments = []
                for tourney in tournaments_data:
                    t_data = {
                        "uuid": tourney.get("id"),
                        "name": tourney.get("name"),
                        "date": parse_date(tourney.get("startDate")),
                        "format": normalize_format(tourney.get("format")),
                        "source": "melee.gg_api",
                        "url": f"https://melee.gg/Tournament/View/{tourney.get('id')}",
                        "decks_count": None # This info may not be in the list endpoint
                    }
                    processed_tournaments.append(Tournament(**t_data))
                
                print(f"Successfully fetched {len(processed_tournaments)} tournaments from the API.")
                return processed_tournaments

        except aiohttp.ClientError as e:
            print(f"API request failed: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return [] 