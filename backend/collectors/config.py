import os
from dotenv import load_dotenv

load_dotenv()

class ScraperConfig:
    """Configuration pour le scraper Metalyzr"""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/metalyzr")
    
    # Scraping settings
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))  # Délai entre requêtes
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    
    # User Agent
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Sites sources
    MTGTOP8_BASE_URL = "https://www.mtgtop8.com"
    MTGGOLDFISH_BASE_URL = "https://www.mtggoldfish.com"
    
    # Formats supportés
    SUPPORTED_FORMATS = [
        "Standard",
        "Modern", 
        "Legacy",
        "Vintage",
        "Pioneer",
        "Pauper"
    ]
    
    # Limites de scraping
    MAX_TOURNAMENTS_PER_RUN = int(os.getenv("MAX_TOURNAMENTS_PER_RUN", "10"))
    MAX_DECKS_PER_TOURNAMENT = int(os.getenv("MAX_DECKS_PER_TOURNAMENT", "100"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "scraper.log")

config = ScraperConfig() 