from datetime import datetime
from typing import Optional

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parses a date string into ISO format."""
    if not date_str:
        return None
    try:
        # Handles formats like "2023-10-25T18:00:00.000Z"
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.isoformat()
    except (ValueError, TypeError):
        return date_str

def normalize_format(format_str: str) -> str:
    """Normalizes the format name."""
    if not isinstance(format_str, str):
        return "Unknown"
    format_mapping = {
        "standard": "Standard",
        "modern": "Modern",
        "pioneer": "Pioneer",
        "legacy": "Legacy",
        "vintage": "Vintage",
        "pauper": "Pauper",
        "commander": "Commander",
    }
    return format_mapping.get(format_str.lower(), format_str.title()) 