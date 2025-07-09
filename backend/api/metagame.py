import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Assuming the service is now initialized in the main app
from backend.main import metagame_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/update")
async def trigger_metagame_update(background_tasks: BackgroundTasks):
    """
    Triggers a background task to update the metagame data from Melee.gg.
    """
    logger.info("Received request to update metagame data.")
    
    async def update_task():
        logger.info("Background task started: Updating metagame data.")
        try:
            # We can specify which formats to update
            await metagame_service.update_metagame_data(formats=["Modern", "Legacy", "Standard"], days=14)
            logger.info("Background task finished: Metagame data update complete.")
        except Exception as e:
            logger.error(f"Background task failed: {e}", exc_info=True)

    background_tasks.add_task(update_task)
    
    return {"message": "Metagame update process started in the background."}

@router.get("/status")
async def get_status():
    """Returns the current status of the MetagameService."""
    return metagame_service.get_service_status()

@router.get("/analysis/metagame_share/{format_name}")
def get_metagame_share(format_name: str, days: int = 14) -> Dict[str, Any]:
    # This endpoint can now be implemented with a real SQL query
    # I will replace the mock data with the actual implementation.
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
        results = metagame_service.db_client.execute_query(query, (format_name, start_date, end_date), fetch="all")
        
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
    """Provides data to build a 95% confidence interval chart for archetype winrates."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # This query now works because the `matches` table is populated.
    query = """
    WITH matches_in_scope AS (
        SELECT m.winner_deck_id, m.deck1_id, m.deck2_id
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.tournament_id
        JOIN formats f ON t.format_id = f.format_id
        WHERE f.format_name = %s AND t.tournament_date BETWEEN %s AND %s
    ),
    archetype_performance AS (
        SELECT 
            a.archetype_name,
            COUNT(d.deck_id) AS total_matches,
            SUM(CASE WHEN d.deck_id = mis.winner_deck_id THEN 1 ELSE 0 END) AS wins
        FROM decks d
        JOIN archetypes a ON d.archetype_id = a.archetype_id
        JOIN (
            SELECT deck1_id as deck_id, winner_deck_id FROM matches_in_scope
            UNION ALL
            SELECT deck2_id as deck_id, winner_deck_id FROM matches_in_scope
        ) mis ON d.deck_id = mis.deck_id
        GROUP BY a.archetype_name
        HAVING COUNT(d.deck_id) > 10 -- Filter for at least 10 matches
    )
    SELECT
        ap.archetype_name,
        ap.total_matches,
        ap.wins,
        (CAST(ap.wins AS FLOAT) / ap.total_matches) AS winrate,
        -- Wilson score interval for confidence
        ((CAST(ap.wins AS FLOAT) / ap.total_matches) + 1.96 * 1.96 / (2 * ap.total_matches) - 
         1.96 * SQRT(((CAST(ap.wins AS FLOAT) / ap.total_matches) * (1 - (CAST(ap.wins AS FLOAT) / ap.total_matches)) + 1.96 * 1.96 / (4 * ap.total_matches)) / ap.total_matches)) / 
         (1 + 1.96 * 1.96 / ap.total_matches) AS ci_lower_bound,
        ((CAST(ap.wins AS FLOAT) / ap.total_matches) + 1.96 * 1.96 / (2 * ap.total_matches) + 
         1.96 * SQRT(((CAST(ap.wins AS FLOAT) / ap.total_matches) * (1 - (CAST(ap.wins AS FLOAT) / ap.total_matches)) + 1.96 * 1.96 / (4 * ap.total_matches)) / ap.total_matches)) / 
         (1 + 1.96 * 1.96 / ap.total_matches) AS ci_upper_bound
    FROM archetype_performance ap
    ORDER BY winrate DESC;
    """
    
    try:
        results = metagame_service.db_client.execute_query(query, (format_name, start_date, end_date), fetch="all")
        analysis_data = [
            {"archetype": row[0], "total_matches": row[1], "wins": row[2], "winrate": row[3], "ci_lower": row[4], "ci_upper": row[5]}
            for row in results
        ]
        return {
            "format": format_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "analysis_type": "winrate_confidence_interval",
            "data": analysis_data
        }
    except Exception as e:
        logger.error(f"Error in winrate confidence analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing winrate analysis.")

@router.get("/analysis/matchup_matrix/{format_name}")
def get_matchup_matrix(format_name: str, days: int = 14) -> Dict[str, Any]:
    """Provides data for a matchup matrix, showing winrates between top archetypes."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # First, find the top archetypes to build the matrix
    top_archetypes_query = """
    SELECT a.archetype_name FROM decks d
    JOIN archetypes a ON d.archetype_id = a.archetype_id
    JOIN tournaments t ON d.tournament_id = t.tournament_id
    JOIN formats f ON t.format_id = f.format_id
    WHERE f.format_name = %s AND t.tournament_date BETWEEN %s AND %s
    GROUP BY a.archetype_name ORDER BY COUNT(d.deck_id) DESC LIMIT 8;
    """
    
    try:
        top_archetypes_results = metagame_service.db_client.execute_query(top_archetypes_query, (format_name, start_date, end_date), fetch="all")
        top_archetypes = [row[0] for row in top_archetypes_results]
        if not top_archetypes:
            return {"format": format_name, "data": {"archetypes": [], "matrix": []}}

        # Now, build the matchup query
        matchup_query = """
        WITH pairings AS (
            SELECT
                a1.archetype_name as archetype1,
                a2.archetype_name as archetype2,
                CASE WHEN m.winner_deck_id = m.deck1_id THEN a1.archetype_name ELSE a2.archetype_name END as winner_archetype
            FROM matches m
            JOIN decks d1 ON m.deck1_id = d1.deck_id
            JOIN archetypes a1 ON d1.archetype_id = a1.archetype_id
            JOIN decks d2 ON m.deck2_id = d2.deck_id
            JOIN archetypes a2 ON d2.archetype_id = a2.archetype_id
            JOIN tournaments t ON m.tournament_id = t.tournament_id
            JOIN formats f ON t.format_id = f.format_id
            WHERE f.format_name = %s AND t.tournament_date BETWEEN %s AND %s
            AND a1.archetype_name = ANY(%s) AND a2.archetype_name = ANY(%s)
        )
        SELECT
            p.archetype1,
            p.archetype2,
            COUNT(*) as total_matches,
            SUM(CASE WHEN p.winner_archetype = p.archetype1 THEN 1 ELSE 0 END) as archetype1_wins
        FROM pairings p
        GROUP BY p.archetype1, p.archetype2;
        """
        
        matchup_results = metagame_service.db_client.execute_query(matchup_query, (format_name, start_date, end_date, top_archetypes, top_archetypes), fetch="all")

        # Create a matrix initialized with 0.5 (or 0 for no data)
        matrix_map = {(a1, a2): {"matches": 0, "wins": 0} for a1 in top_archetypes for a2 in top_archetypes}
        
        for row in matchup_results:
            a1, a2, total, a1_wins = row
            # To handle both (A,B) and (B,A) pairings, we update both sides
            if (a1, a2) in matrix_map:
                matrix_map[(a1, a2)]["matches"] += total
                matrix_map[(a1, a2)]["wins"] += a1_wins
            if (a2, a1) in matrix_map:
                matrix_map[(a2, a1)]["matches"] += total
                matrix_map[(a2, a1)]["wins"] += (total - a1_wins)

        final_matrix = [
            [
                0.5 if a1 == a2 else (matrix_map[(a1,a2)]["wins"] / matrix_map[(a1,a2)]["matches"] if matrix_map[(a1,a2)]["matches"] > 0 else 0)
                for a2 in top_archetypes
            ]
            for a1 in top_archetypes
        ]

        return {
            "format": format_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "analysis_type": "matchup_matrix",
            "data": {
                "archetypes": top_archetypes,
                "matrix": final_matrix
            }
        }
    except Exception as e:
        logger.error(f"Error in matchup matrix analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing matchup matrix.") 