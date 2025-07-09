"""
Intégration réelle avec les scrapers MTG
Basée sur fbettega/mtg_decklist_scrapper et autres projets similaires
"""
import json
import logging
import httpx
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class MTGScraper:
    """Scraper universel pour sites MTG"""
    
    def __init__(self, cache_dir: str = "cache/scraper"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers pour éviter les blocages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.http_client = httpx.Client(
            timeout=30.0,
            headers=self.headers,
            follow_redirects=True
        )
        
        # Sites supportés
        self.supported_sites = {
            'mtggoldfish.com': self._scrape_mtggoldfish,
            'mtgtop8.com': self._scrape_mtgtop8,
            'edhrec.com': self._scrape_edhrec,
            'aetherhub.com': self._scrape_aetherhub,
            'archidekt.com': self._scrape_archidekt,
            'moxfield.com': self._scrape_moxfield,
            'tappedout.net': self._scrape_tappedout
        }
    
    def _get_cache_file(self, url: str) -> Path:
        """Obtenir le chemin du fichier de cache pour une URL"""
        url_hash = str(hash(url)).replace('-', 'n')
        return self.cache_dir / f"scrape_{url_hash}.json"
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch une page web et retourner BeautifulSoup"""
        try:
            response = self.http_client.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _scrape_mtggoldfish(self, url: str) -> Optional[Dict]:
        """Scraper pour MTGGoldfish"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Extraire le nom du deck
            deck_name = soup.find('h1', class_='deck-view-title')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            # Extraire les cartes
            mainboard = []
            sideboard = []
            
            # Chercher les sections mainboard et sideboard
            deck_sections = soup.find_all('div', class_='deck-view-deck-table')
            
            for section in deck_sections:
                section_title = section.find('h4')
                if not section_title:
                    continue
                    
                is_sideboard = 'sideboard' in section_title.text.lower()
                target_list = sideboard if is_sideboard else mainboard
                
                # Extraire les cartes de cette section
                card_rows = section.find_all('tr')
                for row in card_rows:
                    qty_cell = row.find('td', class_='deck-col-qty')
                    name_cell = row.find('td', class_='deck-col-card')
                    
                    if qty_cell and name_cell:
                        try:
                            qty = int(qty_cell.text.strip())
                            name = name_cell.text.strip()
                            target_list.append({"name": name, "count": qty})
                        except ValueError:
                            continue
            
            return {
                "name": deck_name,
                "source": "mtggoldfish.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping MTGGoldfish {url}: {e}")
            return None
    
    def _scrape_mtgtop8(self, url: str) -> Optional[Dict]:
        """Scraper pour MTGTop8"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Extraire le nom du deck
            deck_name = soup.find('div', class_='deck_title')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            # Extraire les cartes
            mainboard = []
            sideboard = []
            
            # MTGTop8 a une structure différente
            deck_tables = soup.find_all('table', class_='Stable')
            
            for table in deck_tables:
                rows = table.find_all('tr')
                current_list = mainboard  # Par défaut mainboard
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Vérifier si c'est une section sideboard
                        if 'sideboard' in row.text.lower():
                            current_list = sideboard
                            continue
                        
                        # Extraire quantité et nom
                        qty_text = cells[0].text.strip()
                        name_text = cells[1].text.strip()
                        
                        if qty_text.isdigit() and name_text:
                            current_list.append({
                                "name": name_text,
                                "count": int(qty_text)
                            })
            
            return {
                "name": deck_name,
                "source": "mtgtop8.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping MTGTop8 {url}: {e}")
            return None
    
    def _scrape_edhrec(self, url: str) -> Optional[Dict]:
        """Scraper pour EDHRec"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Structure spécifique à EDHRec
            deck_name = soup.find('h1', class_='title')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            mainboard = []
            
            # EDHRec utilise une structure différente
            card_sections = soup.find_all('div', class_='card-section')
            
            for section in card_sections:
                cards = section.find_all('div', class_='card')
                for card in cards:
                    qty_elem = card.find('span', class_='quantity')
                    name_elem = card.find('a', class_='card-name')
                    
                    if qty_elem and name_elem:
                        try:
                            qty = int(qty_elem.text.strip())
                            name = name_elem.text.strip()
                            mainboard.append({"name": name, "count": qty})
                        except ValueError:
                            continue
            
            return {
                "name": deck_name,
                "source": "edhrec.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": [],
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping EDHRec {url}: {e}")
            return None
    
    def _scrape_aetherhub(self, url: str) -> Optional[Dict]:
        """Scraper pour AetherHub"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Structure basique pour AetherHub
            deck_name = soup.find('h1')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            mainboard = []
            sideboard = []
            
            # Rechercher les sections de cartes
            card_sections = soup.find_all('div', class_='cardlist')
            
            for section in card_sections:
                is_sideboard = 'sideboard' in section.get('class', [])
                target_list = sideboard if is_sideboard else mainboard
                
                cards = section.find_all('div', class_='cardentry')
                for card in cards:
                    qty_match = re.search(r'(\d+)', card.text)
                    name_match = re.search(r'\d+\s+(.+)', card.text)
                    
                    if qty_match and name_match:
                        qty = int(qty_match.group(1))
                        name = name_match.group(1).strip()
                        target_list.append({"name": name, "count": qty})
            
            return {
                "name": deck_name,
                "source": "aetherhub.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping AetherHub {url}: {e}")
            return None
    
    def _scrape_archidekt(self, url: str) -> Optional[Dict]:
        """Scraper pour Archidekt"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Structure basique pour Archidekt
            deck_name = soup.find('h1', class_='deck-title')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            mainboard = []
            
            # Archidekt utilise souvent du JavaScript, donc structure simplifiée
            card_elements = soup.find_all('div', class_='card-entry')
            
            for card in card_elements:
                qty_elem = card.find('span', class_='quantity')
                name_elem = card.find('a', class_='card-name')
                
                if qty_elem and name_elem:
                    try:
                        qty = int(qty_elem.text.strip())
                        name = name_elem.text.strip()
                        mainboard.append({"name": name, "count": qty})
                    except ValueError:
                        continue
            
            return {
                "name": deck_name,
                "source": "archidekt.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": [],
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Archidekt {url}: {e}")
            return None
    
    def _scrape_moxfield(self, url: str) -> Optional[Dict]:
        """Scraper pour Moxfield"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Structure basique pour Moxfield
            deck_name = soup.find('h1', class_='deck-name')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            mainboard = []
            sideboard = []
            
            # Moxfield utilise beaucoup de JavaScript
            # Structure simplifiée pour le scraping
            card_sections = soup.find_all('div', class_='deck-section')
            
            for section in card_sections:
                section_title = section.find('h3')
                is_sideboard = section_title and 'sideboard' in section_title.text.lower()
                target_list = sideboard if is_sideboard else mainboard
                
                cards = section.find_all('div', class_='card-row')
                for card in cards:
                    qty_elem = card.find('span', class_='quantity')
                    name_elem = card.find('a', class_='card-name')
                    
                    if qty_elem and name_elem:
                        try:
                            qty = int(qty_elem.text.strip())
                            name = name_elem.text.strip()
                            target_list.append({"name": name, "count": qty})
                        except ValueError:
                            continue
            
            return {
                "name": deck_name,
                "source": "moxfield.com",
                "url": url,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Moxfield {url}: {e}")
            return None
    
    def _scrape_tappedout(self, url: str) -> Optional[Dict]:
        """Scraper pour TappedOut"""
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # Structure basique pour TappedOut
            deck_name = soup.find('h1', class_='deck-title')
            deck_name = deck_name.text.strip() if deck_name else "Unknown Deck"
            
            mainboard = []
            sideboard = []
            
            # TappedOut structure
            board_sections = soup.find_all('div', class_='board-container')
            
            for section in board_sections:
                section_title = section.find('h4')
                is_sideboard = section_title and 'sideboard' in section_title.text.lower()
                target_list = sideboard if is_sideboard else mainboard
                
                cards = section.find_all('li', class_='card')
                for card in cards:
                    qty_elem = card.find('span', class_='qty')
                    name_elem = card.find('a', class_='card-name')
                    
                    if qty_elem and name_elem:
                        try:
                            qty = int(qty_elem.text.strip())
                            name = name_elem.text.strip()
                            target_list.append({"name": name, "count": qty})
                        except ValueError:
                            continue
            
            return {
                "name": deck_name,
                "source": "tappedout.net",
                "url": url,
                "mainboard": mainboard,
                "sideboard": sideboard,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping TappedOut {url}: {e}")
            return None
    
    def scrape_deck(self, url: str, use_cache: bool = True) -> Optional[Dict]:
        """Scraper un deck depuis une URL"""
        cache_file = self._get_cache_file(url)
        
        # Vérifier le cache
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                logger.info(f"Loaded deck from cache: {url}")
                return cached_data
            except Exception as e:
                logger.warning(f"Error loading cache for {url}: {e}")
        
        # Déterminer le site
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Trouver le scraper approprié
        scraper_func = None
        for site, scraper in self.supported_sites.items():
            if site in domain:
                scraper_func = scraper
                break
        
        if not scraper_func:
            logger.error(f"No scraper found for domain: {domain}")
            return None
        
        # Scraper le deck
        logger.info(f"Scraping deck from {url}")
        deck_data = scraper_func(url)
        
        if not deck_data:
            logger.error(f"Failed to scrape deck from {url}")
            return None
        
        # Sauvegarder en cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(deck_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached deck data for {url}")
        except Exception as e:
            logger.warning(f"Error caching deck data for {url}: {e}")
        
        return deck_data
    
    def scrape_multiple_decks(self, urls: List[str], use_cache: bool = True) -> List[Dict]:
        """Scraper plusieurs decks"""
        results = []
        
        for url in urls:
            deck_data = self.scrape_deck(url, use_cache)
            if deck_data:
                results.append(deck_data)
        
        return results
    
    def get_supported_sites(self) -> List[str]:
        """Obtenir la liste des sites supportés"""
        return list(self.supported_sites.keys())
    
    def close(self):
        """Fermer le client HTTP"""
        self.http_client.close() 