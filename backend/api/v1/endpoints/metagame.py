from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from backend import crud, models, schemas
from backend.database import SessionLocal
from backend.collectors.melee_playwright_collector import fetch_tournaments_from_melee

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tournaments", response_model=List[schemas.Tournament])
async def read_tournaments(request: Request, db: Session = Depends(get_db)):
    """
    Scrapes the latest tournaments, stores them, and returns the result.
    """
    browser = request.app.state.browser
    if not browser:
        raise HTTPException(status_code=500, detail="Playwright browser not available.")
    
    # 1. Fetch fresh data using the collector
    print("Fetching new tournament data from Melee.gg...")
    tournaments_data = await fetch_tournaments_from_melee(browser, format_name="Modern", limit=5)
    
    if not tournaments_data:
        print("No new tournaments found.")
        # Even if no new tournaments, still return what's in the DB
        return crud.get_tournaments(db, skip=0, limit=100)

    # 2. Save new tournaments to the database
    print(f"Saving {len(tournaments_data)} new tournaments to the database...")
    for t_data in tournaments_data:
        crud.create_tournament(db=db, tournament=t_data)
        
    # 3. Return all tournaments from the database
    return crud.get_tournaments(db, skip=0, limit=100) 