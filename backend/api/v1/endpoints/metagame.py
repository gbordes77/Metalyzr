from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend import crud, schemas
from backend.database import get_db

router = APIRouter()

@router.get(
    "/",
    response_model=List[schemas.MetagameShare],
    summary="Get Metagame Breakdown",
    description="Returns the percentage share of each archetype in a given format, optionally filtered by a start date.",
)
def get_metagame_breakdown(
    format_name: str = Query(..., description="The game format, e.g., 'Modern' or 'Standard'"),
    start_date: Optional[date] = Query(None, description="The start date for the analysis (YYYY-MM-DD)."),
    db: Session = Depends(get_db)
):
    """
    Retrieves the metagame share for a specific format.

    - **format_name**: The competitive format to analyze.
    - **start_date**: Optional filter to only include tournaments from this date onwards.
    - **db**: Database session dependency.
    """
    try:
        metagame_data = crud.get_metagame_by_format(
            db, format_name=format_name, start_date=str(start_date) if start_date else None
        )
        if not metagame_data:
            raise HTTPException(
                status_code=404,
                detail=f"No metagame data found for format: {format_name}",
            )
        return metagame_data
    except Exception as e:
        # In a real app, you'd have more specific error handling and logging
        raise HTTPException(status_code=500, detail="Internal Server Error") 