"""
Gestionnaire de cache pour MTGODecklistCache
Télécharge et synchronise automatiquement les données depuis GitHub
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import os

class MTGOCacheManager:
    """Gestionnaire du cache MTGODecklistCache"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.logger = logging.getLogger("cache.mtgo")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # URLs du cache GitHub
        self.base_url = "https://raw.githubusercontent.com/Jiliac/MTGODecklistCache/main"
        self.tournaments_url = f"{self.base_url}/Tournaments"
        self.archive_url = f"{self.base_url}/Tournaments-Archive"
        
        # Configuration
        self.update_interval = timedelta(hours=6)  # Sync toutes les 6h
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cache en mémoire
        self._tournaments_cache: Dict[str, Any] = {}
        self._archive_cache: Dict[str, Any] = {}
        self._last_update: Optional[datetime] = None
        
    async def __aenter__(self):
        """Initialiser la session HTTP"""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
    
    async def initialize(self) -> bool:
        """Initialiser le cache avec les données récentes"""
        self.logger.info("Initializing MTGODecklistCache...")
        
        try:
            # Charger le cache local s'il existe
            await self._load_local_cache()
            
            # Vérifier si mise à jour nécessaire
            if self._needs_update():
                await self.sync_from_remote()
            
            self.logger.info(f"Cache initialized with {len(self._tournaments_cache)} active tournaments")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache: {e}")
            return False
    
    def _needs_update(self) -> bool:
        """Vérifie si le cache doit être mis à jour"""
        if not self._last_update:
            return True
        
        return datetime.now() - self._last_update > self.update_interval
    
    async def sync_from_remote(self) -> bool:
        """Synchronise les données depuis GitHub"""
        self.logger.info("Syncing MTGODecklistCache from GitHub...")
        
        try:
            if not self.session:
                async with self:
                    return await self._perform_sync()
            else:
                return await self._perform_sync()
                
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            return False
    
    async def _perform_sync(self) -> bool:
        """Effectue la synchronisation"""
        # 1. Télécharger la liste des fichiers actuels
        current_files = await self._fetch_file_list(self.tournaments_url)
        
        if not current_files:
            self.logger.warning("No current tournament files found")
            return False
        
        # 2. Télécharger les tournois récents (derniers 30 jours)
        recent_files = [f for f in current_files if self._is_recent_file(f)]
        
        self.logger.info(f"Downloading {len(recent_files)} recent tournament files...")
        
        for file_name in recent_files[:50]:  # Limite pour éviter surcharge
            tournament_data = await self._download_tournament_file(file_name)
            if tournament_data:
                self._tournaments_cache[file_name] = tournament_data
        
        # 3. Sauvegarder le cache localement
        await self._save_local_cache()
        
        self._last_update = datetime.now()
        self.logger.info("Sync completed successfully")
        return True
    
    async def _fetch_file_list(self, base_url: str) -> List[str]:
        """Récupère la liste des fichiers disponibles"""
        try:
            # Utiliser l'API GitHub pour lister les fichiers
            api_url = base_url.replace(
                "raw.githubusercontent.com", 
                "api.github.com/repos"
            ).replace("/main/", "/contents/")
            
            response = await self.session.get(api_url)
            if response.status != 200:
                return []
            
            files_data = await response.json()
            return [f["name"] for f in files_data if f["type"] == "file" and f["name"].endswith(".json")]
            
        except Exception as e:
            self.logger.error(f"Error fetching file list: {e}")
            return []
    
    def _is_recent_file(self, filename: str) -> bool:
        """Vérifie si un fichier est récent basé sur son nom"""
        try:
            # Les fichiers sont nommés avec format YYYY-MM-DD
            # Ex: 2025-01-08_modern_tournament.json
            if "_" in filename:
                date_part = filename.split("_")[0]
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                cutoff = datetime.now() - timedelta(days=30)
                return file_date >= cutoff
        except:
            pass
        return True  # Si on ne peut pas parser, on inclut par défaut
    
    async def _download_tournament_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Télécharge un fichier de tournoi spécifique"""
        try:
            url = f"{self.tournaments_url}/{filename}"
            response = await self.session.get(url)
            
            if response.status == 200:
                data = await response.json()
                self.logger.debug(f"Downloaded {filename}")
                return data
            else:
                self.logger.warning(f"Failed to download {filename}: HTTP {response.status}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading {filename}: {e}")
            return None
    
    async def _load_local_cache(self):
        """Charge le cache local s'il existe"""
        cache_file = self.cache_dir / "tournaments_cache.json"
        metadata_file = self.cache_dir / "cache_metadata.json"
        
        try:
            if cache_file.exists() and metadata_file.exists():
                with open(cache_file, 'r') as f:
                    self._tournaments_cache = json.load(f)
                
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self._last_update = datetime.fromisoformat(metadata.get("last_update", ""))
                
                self.logger.info(f"Loaded local cache with {len(self._tournaments_cache)} tournaments")
                
        except Exception as e:
            self.logger.warning(f"Could not load local cache: {e}")
    
    async def _save_local_cache(self):
        """Sauvegarde le cache localement"""
        try:
            cache_file = self.cache_dir / "tournaments_cache.json" 
            metadata_file = self.cache_dir / "cache_metadata.json"
            
            with open(cache_file, 'w') as f:
                json.dump(self._tournaments_cache, f, indent=2, default=str)
            
            metadata = {
                "last_update": self._last_update.isoformat() if self._last_update else None,
                "tournament_count": len(self._tournaments_cache),
                "cache_version": "1.0"
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            self.logger.debug("Local cache saved")
            
        except Exception as e:
            self.logger.error(f"Error saving local cache: {e}")
    
    async def get_tournaments(self, 
                             format_filter: Optional[str] = None,
                             limit: int = 50,
                             include_archive: bool = False) -> List[Dict[str, Any]]:
        """Récupère les tournois filtrés"""
        if not self._tournaments_cache and not await self.initialize():
            return []
        
        tournaments = []
        
        # Convertir le cache en liste de tournois
        for filename, tournament_data in self._tournaments_cache.items():
            try:
                # Standardiser le format de données
                tournament = self._normalize_tournament_data(tournament_data, filename)
                
                # Filtrer par format si spécifié
                if format_filter and not self._matches_format(tournament, format_filter):
                    continue
                
                tournaments.append(tournament)
                
            except Exception as e:
                self.logger.warning(f"Error processing tournament {filename}: {e}")
        
        # Trier par date (plus récent en premier)
        tournaments.sort(key=lambda t: t.get("date", ""), reverse=True)
        
        return tournaments[:limit]
    
    def _normalize_tournament_data(self, raw_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Normalise les données d'un tournoi au format Metalyzr"""
        try:
            # Structure basique du tournoi
            tournament = {
                "name": raw_data.get("name", f"Tournament {filename}"),
                "format": self._extract_format_from_filename(filename),
                "date": self._extract_date_from_filename(filename),
                "source": "mtgo_cache",
                "source_url": f"https://github.com/Jiliac/MTGODecklistCache/blob/main/Tournaments/{filename}",
                "organizer": "MTGO",
                "total_players": len(raw_data.get("decks", [])),
                "decks": [],
                "is_complete": True
            }
            
            # Convertir les decks
            for i, deck_data in enumerate(raw_data.get("decks", [])):
                deck = {
                    "position": i + 1,
                    "player_name": deck_data.get("player", f"Player {i+1}"),
                    "wins": deck_data.get("wins", 0),
                    "losses": deck_data.get("losses", 0),
                    "draws": deck_data.get("draws", 0),
                    "mainboard": deck_data.get("mainboard", {}),
                    "sideboard": deck_data.get("sideboard", {}),
                    "archetype": deck_data.get("archetype", "Unknown"),
                    "color_identity": self._extract_colors(deck_data.get("mainboard", {}))
                }
                tournament["decks"].append(deck)
            
            return tournament
            
        except Exception as e:
            self.logger.error(f"Error normalizing tournament data: {e}")
            return {}
    
    def _extract_format_from_filename(self, filename: str) -> str:
        """Extrait le format depuis le nom de fichier"""
        filename_lower = filename.lower()
        
        format_keywords = {
            "modern": "Modern",
            "standard": "Standard", 
            "legacy": "Legacy",
            "vintage": "Vintage",
            "pioneer": "Pioneer",
            "pauper": "Pauper"
        }
        
        for keyword, format_name in format_keywords.items():
            if keyword in filename_lower:
                return format_name
        
        return "Unknown"
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extrait la date depuis le nom de fichier"""
        try:
            # Format: YYYY-MM-DD_format_tournament.json
            if "_" in filename:
                date_part = filename.split("_")[0]
                # Valider le format de date
                datetime.strptime(date_part, "%Y-%m-%d")
                return date_part
        except:
            pass
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _matches_format(self, tournament: Dict[str, Any], format_filter: str) -> bool:
        """Vérifie si un tournoi correspond au format demandé"""
        tournament_format = tournament.get("format", "").lower()
        filter_format = format_filter.lower()
        return filter_format in tournament_format
    
    def _extract_colors(self, mainboard: Dict[str, int]) -> str:
        """Extrait l'identité colorielle depuis un mainboard"""
        # Logique simplifiée - dans la réalité on aurait une DB de cartes
        colors = set()
        
        # Cartes connues et leurs couleurs (exemple limité)
        known_colors = {
            "lightning bolt": "R",
            "counterspell": "U",
            "swords to plowshares": "W", 
            "dark ritual": "B",
            "giant growth": "G",
            "tarmogoyf": "G",
            "snapcaster mage": "U"
        }
        
        for card_name in mainboard.keys():
            card_lower = card_name.lower()
            for known_card, color in known_colors.items():
                if known_card in card_lower:
                    colors.add(color)
        
        return "".join(sorted(colors)) if colors else "C"
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        if not self._tournaments_cache:
            await self.initialize()
        
        stats = {
            "total_tournaments": len(self._tournaments_cache),
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "cache_size_mb": await self._calculate_cache_size(),
            "formats": {},
            "date_range": {"oldest": None, "newest": None}
        }
        
        # Analyser les formats et dates
        dates = []
        for filename, data in self._tournaments_cache.items():
            format_name = self._extract_format_from_filename(filename)
            stats["formats"][format_name] = stats["formats"].get(format_name, 0) + 1
            
            date_str = self._extract_date_from_filename(filename)
            dates.append(date_str)
        
        if dates:
            dates.sort()
            stats["date_range"]["oldest"] = dates[0]
            stats["date_range"]["newest"] = dates[-1]
        
        return stats
    
    async def _calculate_cache_size(self) -> float:
        """Calcule la taille du cache en MB"""
        try:
            cache_file = self.cache_dir / "tournaments_cache.json"
            if cache_file.exists():
                size_bytes = cache_file.stat().st_size
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return 0.0

# Instance globale
mtgo_cache_manager = MTGOCacheManager() 