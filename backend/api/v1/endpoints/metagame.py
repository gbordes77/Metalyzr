from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from backend import crud, models, schemas
from backend.database import SessionLocal
from backend.collectors.melee_api_collector import fetch_tournaments_from_api

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tournaments_from_api", response_model=List[schemas.Tournament])
async def read_tournaments_from_api(db: Session = Depends(get_db)):
    """
    (TEST ENDPOINT)
    Scrapes the latest tournaments from the official API, stores them, and returns the result.
    """
    print("Fetching new tournament data from Melee.gg OFFICIAL API...")
    tournaments_data = await fetch_tournaments_from_api(format_name="Modern", limit=10)
    
    if not tournaments_data:
        print("No new tournaments found from the API.")
        raise HTTPException(status_code=404, detail="No tournaments found from the official API.")

    # Save new tournaments to the database
    print(f"Saving {len(tournaments_data)} new tournaments to the database...")
    for t_data in tournaments_data:
        # The data is already a Tournament schema object from the collector
        crud.create_tournament(db=db, tournament=t_data)
        
    # Return all tournaments from the database
    return crud.get_tournaments(db, skip=0, limit=100) 