import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Iterator

logger = logging.getLogger(__name__)

class DecklistCacheReader:
    """
    Reads tournament data from the file-based MTG_decklistcache.
    The structure is expected to be: <cache_root>/<source>/<year>/<month>/<day>/<tournament_file>.json
    """
    def __init__(self, cache_root: str = "data/MTG_decklistcache"):
        self.cache_path = Path(cache_root)
        if not self.cache_path.exists() or not self.cache_path.is_dir():
            raise FileNotFoundError(f"The cache directory was not found at {cache_root}")

    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Reads a single JSON file and returns its content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read or parse {file_path}: {e}")
            return {}

    def get_all_tournaments(self) -> Iterator[Dict[str, Any]]:
        """
        Walks the cache directory and yields tournament data from each JSON file.
        """
        logger.info(f"Starting to read tournaments from cache at {self.cache_path}...")
        if not self.cache_path.exists():
            logger.error("Cache path does not exist.")
            return

        for file_path in self.cache_path.glob('**/*.json'):
            if "archetype" in file_path.name:
                continue # Skip archetype definition files for now

            tournament_data = self._read_json_file(file_path)
            if tournament_data:
                # Add source from file path, as it's not in the JSON
                try:
                    source = file_path.parts[-5]
                    tournament_data['source'] = source
                except IndexError:
                     tournament_data['source'] = 'unknown'
                yield tournament_data 