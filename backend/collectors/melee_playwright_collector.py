import asyncio
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import json

from ..schemas import Tournament
from .utils import parse_date, normalize_format

async def get_tournament_details(page: Page, tournament_id: str) -> Optional[Dict[str, Any]]:
    """Navigates to a tournament page and extracts its JSON data."""
    print(f"Fetching details for tournament ID: {tournament_id}...")
    url = f"https://melee.gg/Tournament/View/{tournament_id}"
    try:
        await page.goto(url, wait_until="domcontentloaded")
        
        script_selector = 'script#tournament-view-model-json'
        script_handle = await page.query_selector(script_selector)
        
        if not script_handle:
            print(f"Could not find data script for tournament {tournament_id}")
            return None
            
        json_data = await script_handle.json_value()
        
        return {
            "uuid": json_data.get("ID"),
            "name": json_data.get("Name"),
            "date": parse_date(json_data.get("StartDate")),
            "format": normalize_format(json_data.get("Format")),
            "source": "melee.gg",
            "url": url,
            "decks_count": len(json_data.get("Decklists", []))
        }
    except Exception as e:
        print(f"Error fetching details for tournament {tournament_id}: {e}")
        return None


async def fetch_tournaments_from_melee(
    browser: Browser, format_name: str = "Modern", limit: int = 5
) -> List[Tournament]:
    """
    Uses Playwright to scrape tournament data from Melee.gg.
    """
    print(f"Starting Playwright scraper for '{format_name}' tournaments...")
    page = await browser.new_page()
    
    # 1. Go to the main tournament list page
    list_url = f"https://melee.gg/Tournaments/Index?game=Magic&format={format_name}"
    await page.goto(list_url, wait_until="networkidle")

    # 2. Extract tournament IDs from the links
    links = await page.query_selector_all('a[href^="/Tournament/View/"]')
    tournament_ids = []
    for link in links:
        href = await link.get_attribute('href')
        if href:
            tid = href.split('/')[-1]
            if tid.isdigit():
                tournament_ids.append(tid)

    if not tournament_ids:
        print("No tournament IDs found on the page.")
        await page.close()
        return []

    print(f"Found {len(tournament_ids)} tournament IDs. Fetching details for the first {limit}...")

    # 3. Fetch details for each tournament
    all_tournaments_data = []
    for tid in tournament_ids[:limit]:
        details = await get_tournament_details(page, tid)
        if details:
            all_tournaments_data.append(Tournament(**details))

    await page.close()
    return all_tournaments_data


async def main():
    """Main function for testing the scraper."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tournaments = await fetch_tournaments_from_melee(browser)
        if tournaments:
            print("\n--- ✅ Extracted Data ---")
            for t in tournaments:
                print(t.model_dump_json(indent=2))
        else:
            print("\n--- ❌ No data was extracted ---")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main()) 