#!/usr/bin/env python3
"""
Script principal du scraper Metalyzr
Orchestre le scraping des différents sites sources
"""

import asyncio
import logging
import argparse
from typing import List

# Make sure the script can find the 'backend' module
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.collectors.config import config
from backend.collectors.mtgtop8_scraper import MTGTop8Scraper
from backend.collectors.melee_api_client import MeleeAPIClient
from backend.collectors.storage import DataStorage

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

async def run_scraper(sources: List[str], formats: List[str], max_tournaments: int):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting collectors for sources: {sources}")
    
    storage = DataStorage()
    
    scrapers = {
        "mtgtop8": MTGTop8Scraper(),
        "melee": MeleeAPIClient()
    }

    for source_name in sources:
        if source_name not in scrapers:
            logger.warning(f"Source '{source_name}' is not supported. Skipping.")
            continue
        
        scraper = scrapers[source_name]
        logger.info(f"Running scraper for source: {source_name}")

        async with scraper:
            try:
                for format_name in formats:
                    logger.info(f"Scraping format '{format_name}' from '{source_name}'...")
                    # Adapt method name for MeleeClient
                    if source_name == 'melee':
                        tournaments = await scraper.get_tournaments(format_name, limit=max_tournaments)
                    else:
                        tournaments = await scraper.scrape_tournaments(format_name, max_tournaments)
                    
                    if not tournaments:
                        logger.warning(f"No tournaments found for format '{format_name}' from '{source_name}'.")
                        continue
                    
                    saved_count = 0
                    for tournament_data in tournaments:
                        if storage.save_tournament_data(tournament_data):
                            saved_count += 1
                    
                    logger.info(f"Successfully saved {saved_count}/{len(tournaments)} tournaments for '{format_name}' from '{source_name}'.")
            except Exception as e:
                logger.error(f"Failed during scraping with {source_name}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Metalyzr Data Collector")
    parser.add_argument(
        "--sources", 
        nargs="+", 
        default=["melee"],
        choices=["melee", "mtgtop8"],
        help="Sources to scrape from."
    )
    parser.add_argument(
        "--formats", 
        nargs="+", 
        default=["Standard"],
        help="Formats to scrape."
    )
    parser.add_argument(
        "--max-tournaments", 
        type=int, 
        default=5,
        help="Maximum number of tournaments per format per source."
    )
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        asyncio.run(run_scraper(args.sources, args.formats, args.max_tournaments))
    except KeyboardInterrupt:
        logger.info("Collector interrupted by user.")
    except Exception:
        logger.error("Collector failed.", exc_info=True)
        
if __name__ == "__main__":
    main() 