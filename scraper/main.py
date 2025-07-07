#!/usr/bin/env python3
"""
Script principal du scraper Metalyzr
Orchestre le scraping des différents sites sources
"""

import asyncio
import logging
import argparse
from datetime import datetime
from typing import List

from config import config
from mtgtop8_scraper import MTGTop8Scraper
from data_manager import DataManager

def setup_logging():
    """Configure le logging global"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.LOG_FILE)
        ]
    )

async def scrape_format(scraper, data_manager, format_name: str, max_tournaments: int):
    """Scrape un format spécifique"""
    logger = logging.getLogger("scraper.main")
    
    logger.info(f"Starting scraping for format: {format_name}")
    
    try:
        # Scraper les tournois
        tournaments = await scraper.scrape_tournaments(format_name, max_tournaments)
        
        if not tournaments:
            logger.warning(f"No tournaments found for format: {format_name}")
            return
        
        # Sauvegarder les données
        saved_count = 0
        for tournament_data in tournaments:
            tournament_id = data_manager.save_tournament_data(tournament_data)
            if tournament_id:
                saved_count += 1
        
        logger.info(f"Successfully saved {saved_count}/{len(tournaments)} tournaments for {format_name}")
        
    except Exception as e:
        logger.error(f"Error scraping format {format_name}: {str(e)}")

async def run_scraper(formats: List[str], max_tournaments: int = 5):
    """Exécute le scraper pour les formats spécifiés"""
    logger = logging.getLogger("scraper.main")
    
    logger.info("Starting Metalyzr scraper")
    logger.info(f"Formats: {formats}")
    logger.info(f"Max tournaments per format: {max_tournaments}")
    
    # Initialiser les composants
    data_manager = DataManager()
    
    # Scraper MTGTop8
    async with MTGTop8Scraper() as scraper:
        # Scraper chaque format
        for format_name in formats:
            await scrape_format(scraper, data_manager, format_name, max_tournaments)
    
    # Afficher les statistiques finales
    stats = data_manager.get_tournament_stats()
    logger.info(f"Scraping completed. Stats: {stats}")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Metalyzr Tournament Scraper")
    parser.add_argument(
        "--formats", 
        nargs="+", 
        default=["Standard", "Modern"],
        choices=config.SUPPORTED_FORMATS,
        help="Formats à scraper"
    )
    parser.add_argument(
        "--max-tournaments", 
        type=int, 
        default=config.MAX_TOURNAMENTS_PER_RUN,
        help="Nombre maximum de tournois par format"
    )
    parser.add_argument(
        "--cleanup", 
        action="store_true",
        help="Nettoyer les anciennes données"
    )
    parser.add_argument(
        "--stats-only", 
        action="store_true",
        help="Afficher seulement les statistiques"
    )
    
    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger("scraper.main")
    
    try:
        if args.stats_only:
            # Afficher les statistiques uniquement
            data_manager = DataManager()
            stats = data_manager.get_tournament_stats()
            print("\n=== STATISTIQUES METALYZR ===")
            print(f"Total tournois: {stats.get('total_tournaments', 0)}")
            print(f"Total decks: {stats.get('total_decks', 0)}")
            print(f"Formats: {stats.get('formats', {})}")
            print(f"Sources: {stats.get('sources', {})}")
            return
        
        if args.cleanup:
            # Nettoyer les anciennes données
            data_manager = DataManager()
            data_manager.cleanup_old_data()
            logger.info("Cleanup completed")
        
        # Exécuter le scraper
        asyncio.run(run_scraper(args.formats, args.max_tournaments))
        
    except KeyboardInterrupt:
        logger.info("Scraper interrupted by user")
    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 