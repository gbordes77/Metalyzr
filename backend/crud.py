from sqlalchemy.orm import Session
from sqlalchemy import func, text
from . import models

def get_metagame_by_format(db: Session, format_name: str, start_date: str = None):
    """
    Performs a full metagame analysis for a given format, optionally filtered by a start date.
    """
    query = (
        db.query(
            models.Archetype.archetype_name,
            func.count(models.Deck.deck_id).label("deck_count")
        )
        .join(models.Deck, models.Archetype.archetype_id == models.Deck.archetype_id)
        .join(models.Tournament, models.Deck.tournament_id == models.Tournament.tournament_id)
        .join(models.Format, models.Tournament.format_id == models.Format.format_id)
        .filter(models.Format.format_name == format_name)
        .filter(models.Archetype.archetype_name != 'Unknown')
    )

    if start_date:
        query = query.filter(models.Tournament.tournament_date >= start_date)

    # Subquery to get the total number of decks for the format and date range
    total_decks_subquery = query.with_entities(func.count(models.Deck.deck_id)).scalar_subquery()

    query = (
        query
        .group_by(models.Archetype.archetype_name)
        .order_by(text("deck_count DESC"))
        .add_columns(
            (func.count(models.Deck.deck_id) * 100.0 / total_decks_subquery).label("prevalence")
        )
    )

    results = query.all()

    return [
        {
            "archetype": row.archetype_name,
            "deck_count": row.deck_count,
            "prevalence": round(row.prevalence, 2) if row.prevalence is not None else 0
        }
        for row in results
    ] 