import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date

from services.metagame_service import MetagameService
from database import DatabaseClient

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Status Tracking ---
# Simple in-memory dict to hold the state of the background task.
# In a larger application, this would be replaced by Redis or a database table.
task_status: Dict[str, Any] = {
    "status": "idle", # idle, running, completed, failed
    "progress": 0,
    "total": 0,
    "message": "",
    "error": None,
}

# --- Client Initialization ---
db_client = DatabaseClient()
# Pass the status dict to the service so it can update it
metagame_service = MetagameService(database_client=db_client, task_status_dict=task_status)

# --- Constants ---
SUPPORTED_FORMATS = [
    "Standard", "Modern", "Legacy", "Vintage", "Pioneer", "Pauper", "Commander", "Limited"
]

# --- API Endpoints ---

@router.get("/population-status")
def get_population_status() -> Dict[str, Any]:
    """
    Returns the current status of the data population background task.
    """
    return task_status

@router.get("/formats")
def get_supported_formats() -> List[str]:
    """
    Returns a list of supported MTG formats for data retrieval.
    """
    return SUPPORTED_FORMATS

@router.post("/populate-database")
async def populate_database(
    background_tasks: BackgroundTasks, 
    format_name: Optional[str] = None, 
    start_date: Optional[date] = None
):
    """
    Endpoint to trigger the full data update process from Melee.gg.
    This is a long-running task executed in the background.
    """
    if task_status["status"] == "running":
        raise HTTPException(status_code=409, detail="A data population task is already in progress.")

    # Reset status and run the task
    task_status.update({"status": "running", "progress": 0, "total": 0, "message": "Initializing...", "error": None})
    background_tasks.add_task(metagame_service.update_metagame_data, format_name=format_name, start_date=start_date)
    return {"message": "Metagame data update started in the background."}

# --- Analysis Endpoints ---

@router.get("/analysis/metagame_share/{format_name}")
def get_metagame_share(format_name: str, days: int = 14) -> Dict[str, Any]:
    logger.info(f"Getting metagame share for {format_name} over the last {days} days.")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = """
    SELECT
        a.archetype_name,
        COUNT(d.deck_id) AS deck_count
    FROM decks d
    JOIN archetypes a ON d.archetype_id = a.archetype_id
    JOIN tournaments t ON d.tournament_id = t.tournament_id
    JOIN formats f ON t.format_id = f.format_id
    WHERE f.format_name = %s AND t.tournament_date BETWEEN %s AND %s
    GROUP BY a.archetype_name
    ORDER BY deck_count DESC;
    """
    
    try:
        results = db_client.execute_query(query, (format_name, start_date, end_date), fetch="all")
        
        total_decks = sum(row[1] for row in results)
        if total_decks == 0:
            return {"format": format_name, "data": []}
            
        analysis_data = [
            {"archetype": row[0], "count": row[1], "share": (row[1] / total_decks) * 100}
            for row in results
        ]
        
        return {
            "format": format_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "analysis_type": "metagame_share",
            "data": analysis_data
        }
    except Exception as e:
        logger.error(f"Error getting metagame share analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing metagame analysis.")


@router.get("/analysis/winrate_confidence/{format_name}")
def get_winrate_confidence(format_name: str, days: int = 14) -> Dict[str, Any]:
    # This implementation is now correct and uses the database
    logger.info(f"Getting winrate confidence for {format_name} over the last {days} days.")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = """
        WITH MatchCounts AS (
            SELECT
                a.archetype_name,
                COUNT(m.match_id) AS total_matches,
                SUM(CASE WHEN m.winner_deck_id = d.deck_id THEN 1 ELSE 0 END) AS wins
            FROM matches m
            JOIN decks d ON d.deck_id = m.deck1_id OR d.deck_id = m.deck2_id
            JOIN archetypes a ON a.archetype_id = d.archetype_id
            JOIN tournaments t ON t.tournament_id = m.tournament_id
            JOIN formats f ON t.format_id = f.format_id
            WHERE f.format_name = %s AND t.tournament_date BETWEEN %s AND %s
            GROUP BY a.archetype_name
        )
        SELECT
            archetype_name,
            (wins::float / total_matches) * 100 AS winrate,
            1.96 * SQRT((wins::float / total_matches) * (1 - (wins::float / total_matches)) / total_matches) * 100 AS confidence_interval
        FROM MatchCounts
        WHERE total_matches > 10 -- Minimum number of matches to be statistically relevant
        ORDER BY winrate DESC;
    """
    try:
        results = db_client.execute_query(query, (format_name, start_date, end_date), fetch="all")
        analysis_data = [
            {
                "archetype": row[0],
                "winrate": row[1],
                "confidence_interval": row[2]
            } for row in results
        ]
        return {
             "format": format_name,
             "analysis_type": "winrate_confidence",
             "data": analysis_data
        }
    except Exception as e:
        logger.error(f"Error getting winrate/confidence analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing winrate analysis.")

@router.get("/analysis/matchup_matrix/{format_name}")
def get_matchup_matrix(format_name: str, days: int = 14) -> Dict[str, Any]:
    logger.info(f"Getting matchup matrix for {format_name} over the last {days} days.")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    query = """
        WITH ArchetypeMatches AS (
            SELECT
                a1.archetype_name AS archetype1,
                a2.archetype_name AS archetype2,
                SUM(CASE WHEN m.winner_deck_id = m.deck1_id THEN 1 ELSE 0 END) AS wins1,
                SUM(CASE WHEN m.winner_deck_id = m.deck2_id THEN 1 ELSE 0 END) AS wins2
            FROM matches m
            JOIN decks d1 ON m.deck1_id = d1.deck_id
            JOIN archetypes a1 ON d1.archetype_id = a1.archetype_id
            JOIN decks d2 ON m.deck2_id = d2.deck_id
            JOIN archetypes a2 ON d2.archetype_id = a2.archetype_id
            JOIN tournaments t ON m.tournament_id = t.tournament_id
            JOIN formats f ON t.format_id = f.format_id
            WHERE f.format_name = %s AND a1.archetype_name != a2.archetype_name AND t.tournament_date BETWEEN %s AND %s
            GROUP BY a1.archetype_name, a2.archetype_name
        )
        SELECT
            archetype1,
            archetype2,
            (wins1::float / (wins1 + wins2)) * 100 AS winrate1
        FROM ArchetypeMatches
        WHERE (wins1 + wins2) > 5; -- Minimum number of matches for a matchup
    """
    try:
        results = db_client.execute_query(query, (format_name, start_date, end_date), fetch="all")
        
        matrix = {}
        all_archetypes = set()
        for row in results:
            a1, a2, wr = row[0], row[1], row[2]
            all_archetypes.add(a1)
            all_archetypes.add(a2)
            if a1 not in matrix: matrix[a1] = {}
            if a2 not in matrix: matrix[a2] = {}
            matrix[a1][a2] = wr
            matrix[a2][a1] = 100 - wr
            
        return {
            "format": format_name,
            "analysis_type": "matchup_matrix",
            "archetypes": sorted(list(all_archetypes)),
            "matrix": matrix
        }
    except Exception as e:
        logger.error(f"Error getting matchup matrix: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing matchup matrix.") 