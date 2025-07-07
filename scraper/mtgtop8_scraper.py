import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

from base_scraper import BaseScraper
from config import config

class MTGTop8Scraper(BaseScraper):
    """Scraper spécialisé pour MTGTop8.com"""
    
    def __init__(self):
        super().__init__("mtgtop8")
        self.base_url = config.MTGTOP8_BASE_URL
        
    async def scrape_tournaments(self, format_name: str, max_tournaments: int = 10) -> List[Dict[str, Any]]:
        """Scrape les tournois MTGTop8 pour un format donné"""
        self.logger.info(f"Scraping tournaments for format: {format_name}")
        
        # URL de recherche MTGTop8 par format
        search_url = f"{self.base_url}/format?f={self._format_to_mtgtop8(format_name)}"
        
        content = await self.fetch_page(search_url)
        if not content:
            self.logger.error(f"Failed to fetch tournaments page for {format_name}")
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        tournaments = []
        
        # Trouver les liens de tournois
        tournament_links = soup.find_all('a', href=re.compile(r'event\?e=\d+'))
        
        for link in tournament_links[:max_tournaments]:
            tournament_url = urljoin(self.base_url, link['href'])
            tournament_data = await self.scrape_tournament_details(tournament_url)
            
            if tournament_data:
                tournaments.append(tournament_data)
                self.logger.info(f"Scraped tournament: {tournament_data['name']}")
        
        self.logger.info(f"Successfully scraped {len(tournaments)} tournaments")
        return tournaments
    
    async def scrape_tournament_details(self, tournament_url: str) -> Optional[Dict[str, Any]]:
        """Scrape les détails d'un tournoi MTGTop8"""
        self.logger.debug(f"Scraping tournament details: {tournament_url}")
        
        content = await self.fetch_page(tournament_url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            # Extraire les informations du tournoi
            title_elem = soup.find('div', class_='event_title')
            name = self.clean_text(title_elem.text) if title_elem else "Unknown Tournament"
            
            # Date du tournoi
            date_elem = soup.find('div', class_='event_date')
            date_str = self.clean_text(date_elem.text) if date_elem else ""
            tournament_date = self.parse_date(date_str) or datetime.now()
            
            # Format
            format_elem = soup.find('div', class_='format')
            format_name = self.clean_text(format_elem.text) if format_elem else "Unknown"
            
            # Localisation
            location_elem = soup.find('div', class_='location')
            location = self.clean_text(location_elem.text) if location_elem else ""
            
            # Nombre de joueurs
            players_elem = soup.find('div', class_='players')
            total_players = self.extract_number(players_elem.text) if players_elem else 0
            
            # Scraper les decks
            decks = await self.scrape_tournament_decks(tournament_url, soup)
            
            tournament_data = {
                "name": name,
                "format": format_name,
                "date": tournament_date,
                "location": location,
                "organizer": "MTGTop8",
                "total_players": total_players,
                "source_url": tournament_url,
                "source_site": "mtgtop8",
                "decks": decks,
                "is_complete": len(decks) > 0
            }
            
            return tournament_data
            
        except Exception as e:
            self.logger.error(f"Error parsing tournament {tournament_url}: {str(e)}")
            return None
    
    async def scrape_tournament_decks(self, tournament_url: str, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Scrape les decks d'un tournoi"""
        decks = []
        
        # Trouver les liens vers les decks
        deck_links = soup.find_all('a', href=re.compile(r'event\?e=\d+&d=\d+'))
        
        for i, link in enumerate(deck_links[:config.MAX_DECKS_PER_TOURNAMENT]):
            deck_url = urljoin(self.base_url, link['href'])
            deck_data = await self.scrape_deck_details(deck_url)
            
            if deck_data:
                deck_data['position'] = i + 1  # Position dans le tournoi
                decks.append(deck_data)
        
        return decks
    
    async def scrape_deck_details(self, deck_url: str) -> Optional[Dict[str, Any]]:
        """Scrape les détails d'un deck MTGTop8"""
        self.logger.debug(f"Scraping deck: {deck_url}")
        
        content = await self.fetch_page(deck_url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            # Nom du joueur
            player_elem = soup.find('div', class_='player_name')
            player_name = self.clean_text(player_elem.text) if player_elem else "Unknown Player"
            
            # Record (wins/losses)
            record_elem = soup.find('div', class_='record')
            wins, losses, draws = self._parse_record(record_elem.text if record_elem else "")
            
            # Composition du deck
            mainboard = self._parse_decklist(soup, 'mainboard')
            sideboard = self._parse_decklist(soup, 'sideboard')
            
            # Couleurs du deck
            color_identity = self._extract_color_identity(mainboard)
            
            deck_data = {
                "player_name": player_name,
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "color_identity": color_identity,
                "total_cards": sum(mainboard.values()) if mainboard else 60
            }
            
            return deck_data
            
        except Exception as e:
            self.logger.error(f"Error parsing deck {deck_url}: {str(e)}")
            return None
    
    def _format_to_mtgtop8(self, format_name: str) -> str:
        """Convertit le nom de format vers l'ID MTGTop8"""
        format_mapping = {
            "Standard": "ST",
            "Modern": "MO", 
            "Legacy": "LE",
            "Vintage": "VI",
            "Pioneer": "PI",
            "Pauper": "PAU"
        }
        return format_mapping.get(format_name, "ST")
    
    def _parse_record(self, record_text: str) -> tuple[int, int, int]:
        """Parse le record d'un joueur (wins-losses-draws)"""
        match = re.search(r'(\d+)-(\d+)(?:-(\d+))?', record_text)
        if match:
            wins = int(match.group(1))
            losses = int(match.group(2))
            draws = int(match.group(3)) if match.group(3) else 0
            return wins, losses, draws
        return 0, 0, 0
    
    def _parse_decklist(self, soup: BeautifulSoup, section: str) -> Dict[str, int]:
        """Parse la composition d'un deck (mainboard ou sideboard)"""
        decklist = {}
        
        # Chercher la section appropriée
        section_div = soup.find('div', class_=section)
        if not section_div:
            return decklist
        
        # Extraire les cartes
        card_rows = section_div.find_all('div', class_='deck_line')
        for row in card_rows:
            count_elem = row.find('span', class_='card_count')
            name_elem = row.find('span', class_='card_name')
            
            if count_elem and name_elem:
                count = self.extract_number(count_elem.text) or 1
                name = self.clean_text(name_elem.text)
                if name:
                    decklist[name] = count
        
        return decklist
    
    def _extract_color_identity(self, mainboard: Dict[str, int]) -> str:
        """Extrait l'identité colorielle d'un deck"""
        # Logique simplifiée - dans un vrai scraper, on utiliserait une base de données de cartes
        colors = set()
        
        # Cartes connues et leurs couleurs (exemple)
        known_cards = {
            "Lightning Bolt": "R",
            "Counterspell": "U", 
            "Swords to Plowshares": "W",
            "Dark Ritual": "B",
            "Giant Growth": "G"
        }
        
        for card_name in mainboard.keys():
            if card_name in known_cards:
                colors.add(known_cards[card_name])
        
        return "".join(sorted(colors)) if colors else "C" 