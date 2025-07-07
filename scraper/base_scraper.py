import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
from asyncio_throttle import Throttler

from config import config

class BaseScraper(ABC):
    """Classe de base pour tous les scrapers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()
        self.session: Optional[aiohttp.ClientSession] = None
        self.throttler = Throttler(rate_limit=config.MAX_CONCURRENT_REQUESTS)
        
    def _setup_logger(self) -> logging.Logger:
        """Configure le logger pour ce scraper"""
        logger = logging.getLogger(f"scraper.{self.name}")
        logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.TIMEOUT),
            headers={"User-Agent": config.USER_AGENT}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, **kwargs) -> Optional[str]:
        """Récupère une page web avec gestion d'erreurs et throttling"""
        async with self.throttler:
            try:
                self.logger.debug(f"Fetching: {url}")
                
                async with self.session.get(url, **kwargs) as response:
                    if response.status == 200:
                        content = await response.text()
                        self.logger.debug(f"Successfully fetched {url} ({len(content)} chars)")
                        return content
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        return None
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout fetching {url}")
                return None
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {str(e)}")
                return None
            finally:
                # Respect du délai entre requêtes
                await asyncio.sleep(config.REQUEST_DELAY)
    
    @abstractmethod
    async def scrape_tournaments(self, format_name: str, max_tournaments: int = 10) -> List[Dict[str, Any]]:
        """Scrape les tournois pour un format donné"""
        pass
    
    @abstractmethod
    async def scrape_tournament_details(self, tournament_url: str) -> Optional[Dict[str, Any]]:
        """Scrape les détails d'un tournoi spécifique"""
        pass
    
    @abstractmethod
    async def scrape_deck_details(self, deck_url: str) -> Optional[Dict[str, Any]]:
        """Scrape les détails d'un deck spécifique"""
        pass
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date depuis différents formats"""
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y", 
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        self.logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte extrait"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\t', ' ')
    
    def extract_number(self, text: str) -> Optional[int]:
        """Extrait un nombre depuis un texte"""
        import re
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None 