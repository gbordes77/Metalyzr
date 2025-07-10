"""
Client API pour Melee.gg
Récupération de données de tournois en temps réel via API officielle
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import os
# from config import config  <- This seems to be an unused and problematic import

class MeleeAPIClient:
    """Client pour l'API Melee.gg"""
    
    def __init__(self):
        self.base_url = "https://melee.gg/api"
        self.logger = logging.getLogger("scraper.melee_api")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Configuration API
        self.headers = {
            "User-Agent": "Metalyzr/1.0 (MTG Meta Analysis)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Rate limiting pour API
        self.request_delay = 1.0  # Plus rapide que scraping
        
    async def __aenter__(self):
        """Initialiser la session HTTP"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
    
    async def get_tournaments(self, 
                            format_name: str = "Modern",
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupérer les tournois Melee.gg pour un format donné
        
        Args:
            format_name: Format MTG (Modern, Standard, etc.)
            start_date: Date de début (défaut: 7 jours ago)
            end_date: Date de fin (défaut: aujourd'hui)
            limit: Nombre max de tournois
        
        Returns:
            Liste des tournois avec métadonnées
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        self.logger.info(f"Fetching Melee.gg tournaments for {format_name}")
        
        # Paramètres de recherche
        params = {
            "game": "magic",
            "format": format_name.lower(),
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "status": "completed",
            "limit": limit
        }
        
        tournaments = []
        
        try:
            url = f"{self.base_url}/tournaments"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parser la réponse API
                    if isinstance(data, dict) and "tournaments" in data:
                        raw_tournaments = data["tournaments"]
                    else:
                        raw_tournaments = data if isinstance(data, list) else []
                    
                    for tournament_data in raw_tournaments:
                        parsed_tournament = await self._parse_tournament(tournament_data)
                        if parsed_tournament:
                            tournaments.append(parsed_tournament)
                            
                    self.logger.info(f"Found {len(tournaments)} tournaments from Melee.gg")
                    
                elif response.status == 429:
                    self.logger.warning("Rate limited by Melee.gg API")
                    await asyncio.sleep(5)  # Attendre avant retry
                    
                else:
                    self.logger.error(f"Melee.gg API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching Melee.gg tournaments: {str(e)}")
        
        return tournaments
    
    async def get_tournament_details(self, tournament_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer les détails complets d'un tournoi
        
        Args:
            tournament_id: ID du tournoi Melee.gg
            
        Returns:
            Données complètes du tournoi avec decks et matchs
        """
        try:
            url = f"{self.base_url}/tournaments/{tournament_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Récupérer aussi les standings/decks et les pairings/matchs
                    standings = await self._get_tournament_standings(tournament_id)
                    pairings = await self._get_tournament_pairings(tournament_id)
                    
                    # Combiner les données
                    tournament_details = await self._parse_tournament_details(data, standings, pairings)
                    return tournament_details
                    
                else:
                    self.logger.error(f"Failed to fetch tournament {tournament_id}: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching tournament details {tournament_id}: {str(e)}")
        
        return None

    async def _get_tournament_pairings(self, tournament_id: str) -> List[Dict[str, Any]]:
        """Récupérer les pairings (matchs) d'un tournoi"""
        try:
            url = f"{self.base_url}/tournaments/{tournament_id}/pairings"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if isinstance(data, list) else data.get("pairings", [])
        except Exception as e:
            self.logger.error(f"Error fetching pairings for {tournament_id}: {str(e)}")
        return []

    async def _get_tournament_standings(self, tournament_id: str) -> List[Dict[str, Any]]:
        """Récupérer les standings/decks d'un tournoi"""
        try:
            url = f"{self.base_url}/tournaments/{tournament_id}/standings"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if isinstance(data, list) else data.get("standings", [])
                    
        except Exception as e:
            self.logger.error(f"Error fetching standings for {tournament_id}: {str(e)}")
        
        return []
    
    async def _parse_tournament(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parser les données brutes d'un tournoi Melee.gg"""
        try:
            # Mapping des champs Melee.gg vers format Metalyzr
            tournament = {
                "id": raw_data.get("id"),
                "name": raw_data.get("name", "Unknown Tournament"),
                "format": self._normalize_format(raw_data.get("format", "")),
                "date": self._parse_date(raw_data.get("startDate") or raw_data.get("date")),
                "location": self._parse_location(raw_data),
                "organizer": raw_data.get("organizer", {}).get("name", "Melee.gg"),
                "total_players": raw_data.get("playerCount", 0),
                "entry_fee": raw_data.get("entryFee"),
                "prize_pool": raw_data.get("prizePool"),
                "source_url": f"https://melee.gg/Tournament/View/{raw_data.get('id')}",
                "source_site": "melee.gg",
                "external_url": f"https://melee.gg/Tournament/View/{raw_data.get('id')}",
                "status": raw_data.get("status", "completed").lower(),
                "is_complete": raw_data.get("status", "").lower() == "completed"
            }
            
            return tournament
            
        except Exception as e:
            self.logger.error(f"Error parsing tournament data: {str(e)}")
            return None
    
    async def _parse_tournament_details(self, tournament_data: Dict[str, Any], 
                                      standings: List[Dict[str, Any]],
                                      pairings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parser les détails complets d'un tournoi avec decks et matchs"""
        
        # Données de base du tournoi
        tournament = await self._parse_tournament(tournament_data)
        if not tournament:
            return {}
        
        # Parser les decks depuis les standings
        decks = []
        player_name_to_deck_id = {}
        for i, standing in enumerate(standings):
            deck = await self._parse_deck(standing, i + 1)
            if deck:
                decks.append(deck)
                # Map player name to a temporary deck ID for match parsing
                player_name_to_deck_id[deck["player_name"]] = i + 1 
        
        tournament["decks"] = decks
        tournament["total_decks"] = len(decks)

        # Parser les matchs depuis les pairings
        matches = []
        for round_data in pairings:
            for match_data in round_data.get("pairings", []):
                match = await self._parse_match(match_data, player_name_to_deck_id)
                if match:
                    matches.append(match)
        
        tournament["matches"] = matches
        
        return tournament
    
    async def _parse_deck(self, standing_data: Dict[str, Any], position: int) -> Optional[Dict[str, Any]]:
        """Parser un deck depuis les données de standings"""
        try:
            player = standing_data.get("player", {})
            deck_data = standing_data.get("deck", {})
            
            deck = {
                "position": position,
                "player_name": player.get("name", f"Player {position}"),
                "wins": standing_data.get("wins", 0),
                "losses": standing_data.get("losses", 0),
                "draws": standing_data.get("draws", 0),
                "points": standing_data.get("points", 0),
                "archetype": deck_data.get("archetype", "Unknown"),
                "mainboard": deck_data.get("mainboard", {}),
                "sideboard": deck_data.get("sideboard", {}),
                "color_identity": deck_data.get("colors", ""),
                "total_cards": sum(deck_data.get("mainboard", {}).values())
            }
            
            return deck
            
        except Exception as e:
            self.logger.error(f"Error parsing deck data: {str(e)}")
            return None

    async def _parse_match(self, match_data: Dict[str, Any], player_name_to_deck_id: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Parser un match depuis les données de pairings"""
        try:
            player1_name = match_data.get("player1", {}).get("name")
            player2_name = match_data.get("player2", {}).get("name")
            winner_name = match_data.get("winner")

            # We need to map player names back to our deck IDs
            deck1_id = player_name_to_deck_id.get(player1_name)
            deck2_id = player_name_to_deck_id.get(player2_name)
            winner_deck_id = player_name_to_deck_id.get(winner_name) if winner_name else None

            if not deck1_id or not deck2_id:
                return None # Skip if we can't identify both players

            return {
                "deck1_id": deck1_id,
                "deck2_id": deck2_id,
                "winner_deck_id": winner_deck_id,
                "result": match_data.get("result", "N/A"),
                "round": match_data.get("round", {}).get("name", "Unknown Round"),
            }

        except Exception as e:
            self.logger.error(f"Error parsing match data: {str(e)}")
            return None

    def _normalize_format(self, format_str: str) -> str:
        """Normaliser le nom de format"""
        format_mapping = {
            "modern": "Modern",
            "standard": "Standard", 
            "legacy": "Legacy",
            "vintage": "Vintage",
            "pioneer": "Pioneer",
            "pauper": "Pauper",
            "commander": "Commander",
            "limited": "Limited"
        }
        
        return format_mapping.get(format_str.lower(), format_str.title())
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parser une date depuis l'API Melee.gg"""
        if not date_str:
            return None
            
        try:
            # Format ISO standard
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(date_str)
        except Exception:
            self.logger.warning(f"Could not parse date: {date_str}")
            return None
    
    def _parse_location(self, tournament_data: Dict[str, Any]) -> str:
        """Parser la localisation du tournoi"""
        location_parts = []
        
        venue = tournament_data.get("venue", {})
        if venue:
            if venue.get("name"):
                location_parts.append(venue["name"])
            if venue.get("city"):
                location_parts.append(venue["city"])
            if venue.get("state"):
                location_parts.append(venue["state"])
            if venue.get("country"):
                location_parts.append(venue["country"])
        
        return ", ".join(location_parts) if location_parts else "Online"

# Configuration pour l'intégration
async def fetch_melee_tournaments(format_name: str = "Modern", max_tournaments: int = 20) -> List[Dict[str, Any]]:
    """
    Function helper pour récupérer les tournois Melee.gg
    Compatible avec l'interface scraper existante
    """
    async with MeleeAPIClient() as client:
        tournaments = await client.get_tournaments(
            format_name=format_name,
            limit=max_tournaments
        )
        
        # Enrichir avec les détails pour chaque tournoi
        detailed_tournaments = []
        for tournament in tournaments:
            if tournament.get("id"):
                details = await client.get_tournament_details(tournament["id"])
                if details:
                    detailed_tournaments.append(details)
                    
                # Rate limiting respectueux
                await asyncio.sleep(client.request_delay)
        
        return detailed_tournaments 