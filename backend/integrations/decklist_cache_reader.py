import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Iterator

logger = logging.getLogger(__name__)

class DecklistCacheReader:
    """
    Reads Magic: The Gathering decklist data from a local cache of JSON files.
    The cache is expected to be a directory containing one JSON file per tournament.
    """
    def __init__(self, cache_root: str = "data/MTG_decklistcache"):
        self.cache_root = cache_root
        if not os.path.isdir(self.cache_root):
            raise FileNotFoundError(f"The cache directory was not found at {self.cache_root}")

    def get_all_tournaments(self) -> Iterator[Dict[str, Any]]:
        """
        Yields all tournaments found in the cache directory, searching recursively.
        """
        for subdir, _, files in os.walk(self.cache_root):
            for filename in files:
                if filename.endswith(".json"):
                    filepath = os.path.join(subdir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            # Let's add the filename as a potential UID, as it's unique
                            data['UID'] = os.path.splitext(filename)[0]

                            # Extract source from the file path, which looks like:
                            # .../Tournaments/{source}/{...}/{file}.json
                            try:
                                path_parts = filepath.split(os.sep)
                                tournaments_index = path_parts.index('Tournaments')
                                if len(path_parts) > tournaments_index + 1:
                                    source = path_parts[tournaments_index + 1]
                                    if 'Tournament' in data and 'Source' not in data['Tournament']:
                                        data['Tournament']['Source'] = source
                            except (ValueError, IndexError):
                                logger.warning(f"Could not extract source from path for {filepath}")

                            yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode JSON from {filepath}")
                    except Exception as e:
                        logger.error(f"Error reading tournament from {filepath}: {e}") 