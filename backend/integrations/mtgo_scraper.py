import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://www.mtgo.com"

def scrape_mtgo_decklists(days: int = 7) -> List[Dict[str, Any]]:
    """
    Scrapes the official MTGO website for recent Standard tournament decklists.
    """
    logger.info(f"Scraping MTGO website for Standard decklists from the last {days} days.")
    decklist_url = f"{BASE_URL}/decklists"
    
    try:
        response = requests.get(decklist_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch MTGO decklist page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Corrected CSS selector based on manual inspection of the website.
    # The decklists are in a div with the id 'decklists-tables'.
    decklist_container = soup.find("div", id="decklists-tables")
    if not decklist_container:
        logger.warning("Could not find the main decklist container on the page (div#decklists-tables).")
        return []

    tournaments = []
    today = datetime.now()
    date_limit = today - timedelta(days=days)

    links = decklist_container.find_all("a")
    logger.info(f"Found {len(links)} potential tournament links. Filtering for recent Standard events.")

    for link in links:
        link_text = link.get_text().strip()
        
        if "standard" not in link_text.lower():
            continue

        # Extract date from the link text (e.g., "Standard League July 10 2025")
        try:
            # This is a bit fragile and depends on MTGO's naming convention
            date_str = " ".join(link_text.split()[-3:])
            event_date = datetime.strptime(date_str, "%B %d %Y")
        except (ValueError, IndexError):
            logger.warning(f"Could not parse date from link text: '{link_text}'")
            continue

        if event_date >= date_limit:
            tournament_data = {
                "name": link_text,
                "url": f"{BASE_URL}{link.get('href')}",
                "date": event_date.strftime("%Y-%m-%d"),
                "source": "MTGO Website"
            }
            tournaments.append(tournament_data)
    
    logger.info(f"Found {len(tournaments)} recent Standard tournaments.")
    return tournaments 