"""
MTGODecklistCache Manager - Gestion du cache Jiliac pour Metalyzr
Intégration avec le repository https://github.com/Jiliac/MTGODecklistCache
"""
import json
import logging
import os
import shutil
import subprocess
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
import aiofiles
import aiohttp

@dataclass
class CachedTournament:
    """Représentation d'un tournoi depuis MTGODecklistCache"""
    name: str
    date: str
    format: str
    source: str
    url: Optional[str] = None
    decks: List[Dict[str, Any]] = field(default_factory=list)
    standings: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheStats:
    """Statistiques du cache MTGODecklistCache"""
    total_tournaments: int = 0
    total_decks: int = 0
    formats_coverage: Dict[str, int] = field(default_factory=dict)
    date_range: Tuple[str, str] = ("", "")
    last_update: Optional[str] = None
    cache_size_mb: float = 0.0

class MTGOCacheManager:
    """
    Gestionnaire du cache MTGODecklistCache pour Metalyzr
    
    Fonctionnalités:
    - Clone et sync du repository Jiliac
    - Parsing des données JSON structurées
    - Filtrage et recherche avancée
    - Intégration avec l'engine Badaro
    - Mise à jour automatique quotidienne
    """
    
    def __init__(self, cache_dir: str = "./mtgo_cache"):
        self.logger = logging.getLogger("mtgo.cache_manager")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Paths du cache
        self.repo_path = self.cache_dir / "MTGODecklistCache"
        self.tournaments_path = self.repo_path / "Tournaments"
        self.archive_path = self.repo_path / "Tournaments-Archive"
        
        # Configuration
        self.repo_url = "https://github.com/Jiliac/MTGODecklistCache.git"
        self.last_sync_file = self.cache_dir / "last_sync.txt"
        
        # Cache des données parsées
        self._tournaments_cache: Dict[str, CachedTournament] = {}
        self._stats_cache: Optional[CacheStats] = None
        self._cache_loaded = False
        
    async def initialize(self, force_clone: bool = False) -> bool:
        """
        Initialiser le cache MTGODecklistCache
        
        Args:
            force_clone: Forcer le clonage même si le repo existe
            
        Returns:
            True si initialisation réussie
        """
        try:
            self.logger.info("🚀 Initializing MTGODecklistCache manager...")
            
            # Cloner ou mettre à jour le repository
            if not self.repo_path.exists() or force_clone:
                await self._clone_repository()
            else:
                await self._update_repository()
            
            # Charger les données en cache
            await self._load_tournaments_cache()
            
            # Calculer les statistiques
            await self._compute_stats()
            
            self._cache_loaded = True
            self.logger.info(f"✅ Cache initialized: {self._stats_cache.total_tournaments} tournaments, {self._stats_cache.total_decks} decks")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize cache: {e}")
            return False
    
    async def _clone_repository(self):
        """Cloner le repository MTGODecklistCache"""
        self.logger.info(f"📥 Cloning MTGODecklistCache from {self.repo_url}...")
        
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)
        
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", self.repo_url, str(self.repo_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            self.logger.info("✅ Repository cloned successfully")
            await self._record_sync_time()
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise Exception(f"Git clone failed: {error_msg}")
    
    async def _update_repository(self):
        """Mettre à jour le repository existant"""
        if not self.repo_path.exists():
            await self._clone_repository()
            return
        
        self.logger.info("🔄 Updating MTGODecklistCache repository...")
        
        process = await asyncio.create_subprocess_exec(
            "git", "pull", "--ff-only",
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            self.logger.info("✅ Repository updated successfully")
            await self._record_sync_time()
        else:
            self.logger.warning(f"⚠️ Git pull failed, falling back to clone: {stderr.decode()}")
            await self._clone_repository()
    
    async def _record_sync_time(self):
        """Enregistrer l'heure de dernière synchronisation"""
        async with aiofiles.open(self.last_sync_file, 'w') as f:
            await f.write(datetime.now().isoformat())
    
    async def _load_tournaments_cache(self):
        """Charger tous les tournois en cache mémoire"""
        self.logger.info("📦 Loading tournaments cache...")
        
        self._tournaments_cache.clear()
        
        # Charger les tournois actifs
        if self.tournaments_path.exists():
            await self._load_tournaments_from_directory(self.tournaments_path, is_archive=False)
        
        # Charger les tournois archivés
        if self.archive_path.exists():
            await self._load_tournaments_from_directory(self.archive_path, is_archive=True)
        
        self.logger.info(f"✅ Loaded {len(self._tournaments_cache)} tournaments in cache")
    
    async def _load_tournaments_from_directory(self, directory: Path, is_archive: bool = False):
        """Charger les tournois depuis un répertoire"""
        
        for source_dir in directory.iterdir():
            if not source_dir.is_dir():
                continue
                
            source_name = source_dir.name
            
            for date_dir in source_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                # Parser les fichiers JSON du jour
                for json_file in date_dir.glob("*.json"):
                    try:
                        tournament = await self._parse_tournament_file(json_file, source_name, is_archive)
                        if tournament:
                            # Clé unique : source_date_name
                            key = f"{source_name}_{tournament.date}_{json_file.stem}"
                            self._tournaments_cache[key] = tournament
                            
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to parse {json_file}: {e}")
    
    async def _parse_tournament_file(self, json_file: Path, source: str, is_archive: bool) -> Optional[CachedTournament]:
        """Parser un fichier de tournoi JSON"""
        
        try:
            async with aiofiles.open(json_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            # Extraire les informations du tournoi
            tournament_info = data.get("Tournament", {})
            
            tournament = CachedTournament(
                name=tournament_info.get("Name", json_file.stem),
                date=tournament_info.get("Date", ""),
                format=tournament_info.get("Format", "Unknown"),
                source=source,
                url=tournament_info.get("Url", ""),
                decks=data.get("Decks", []),
                standings=data.get("Standings", []),
                metadata={
                    "is_archive": is_archive,
                    "file_path": str(json_file),
                    "round_count": tournament_info.get("Rounds", 0),
                    "player_count": len(data.get("Decks", []))
                }
            )
            
            return tournament
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing {json_file}: {e}")
            return None
    
    async def _compute_stats(self):
        """Calculer les statistiques du cache"""
        
        total_tournaments = len(self._tournaments_cache)
        total_decks = 0
        formats_coverage = {}
        dates = []
        
        for tournament in self._tournaments_cache.values():
            total_decks += len(tournament.decks)
            
            # Compter par format
            fmt = tournament.format
            formats_coverage[fmt] = formats_coverage.get(fmt, 0) + 1
            
            # Collecter les dates
            if tournament.date:
                dates.append(tournament.date)
        
        # Calculer la plage de dates
        if dates:
            dates.sort()
            date_range = (dates[0], dates[-1])
        else:
            date_range = ("", "")
        
        # Calculer la taille du cache
        cache_size = 0
        if self.repo_path.exists():
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file():
                    cache_size += file_path.stat().st_size
        
        # Dernière mise à jour
        last_update = None
        if self.last_sync_file.exists():
            last_update = self.last_sync_file.read_text().strip()
        
        self._stats_cache = CacheStats(
            total_tournaments=total_tournaments,
            total_decks=total_decks,
            formats_coverage=formats_coverage,
            date_range=date_range,
            last_update=last_update,
            cache_size_mb=cache_size / (1024 * 1024)
        )
    
    async def get_tournaments(self, 
                            format_filter: Optional[str] = None,
                            source_filter: Optional[str] = None,
                            date_from: Optional[str] = None,
                            date_to: Optional[str] = None,
                            limit: Optional[int] = None,
                            include_archive: bool = True) -> List[CachedTournament]:
        """
        Récupérer les tournois selon des critères
        
        Args:
            format_filter: Filtrer par format (Modern, Standard, etc.)
            source_filter: Filtrer par source (mtgo, melee, etc.)
            date_from: Date minimum (YYYY-MM-DD)
            date_to: Date maximum (YYYY-MM-DD)
            limit: Nombre maximum de résultats
            include_archive: Inclure les tournois archivés
            
        Returns:
            Liste des tournois correspondants
        """
        if not self._cache_loaded:
            await self.initialize()
        
        results = []
        
        for tournament in self._tournaments_cache.values():
            # Filtres
            if format_filter and tournament.format != format_filter:
                continue
            
            if source_filter and tournament.source != source_filter:
                continue
            
            if not include_archive and tournament.metadata.get("is_archive", False):
                continue
            
            if date_from and tournament.date < date_from:
                continue
            
            if date_to and tournament.date > date_to:
                continue
            
            results.append(tournament)
        
        # Trier par date décroissante
        results.sort(key=lambda t: t.date, reverse=True)
        
        # Appliquer la limite
        if limit:
            results = results[:limit]
        
        return results
    
    async def get_decks(self,
                       format_filter: Optional[str] = None,
                       archetype_filter: Optional[str] = None,
                       player_filter: Optional[str] = None,
                       min_wins: Optional[int] = None,
                       limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupérer les decks selon des critères
        
        Args:
            format_filter: Filtrer par format
            archetype_filter: Filtrer par archétype
            player_filter: Filtrer par nom de joueur
            min_wins: Nombre minimum de victoires
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des decks correspondants
        """
        if not self._cache_loaded:
            await self.initialize()
        
        results = []
        
        for tournament in self._tournaments_cache.values():
            if format_filter and tournament.format != format_filter:
                continue
            
            for deck in tournament.decks:
                # Enrichir le deck avec les infos du tournoi
                enriched_deck = {
                    **deck,
                    "tournament_name": tournament.name,
                    "tournament_date": tournament.date,
                    "tournament_format": tournament.format,
                    "tournament_source": tournament.source
                }
                
                # Filtres sur le deck
                if archetype_filter:
                    deck_archetype = deck.get("Archetype", "")
                    if archetype_filter.lower() not in deck_archetype.lower():
                        continue
                
                if player_filter:
                    player_name = deck.get("Player", "")
                    if player_filter.lower() not in player_name.lower():
                        continue
                
                if min_wins is not None:
                    wins = self._extract_wins_from_result(deck.get("Result", ""))
                    if wins < min_wins:
                        continue
                
                results.append(enriched_deck)
        
        # Trier par date de tournoi décroissante
        results.sort(key=lambda d: d.get("tournament_date", ""), reverse=True)
        
        # Appliquer la limite
        if limit:
            results = results[:limit]
        
        return results
    
    def _extract_wins_from_result(self, result_str: str) -> int:
        """Extraire le nombre de victoires depuis une string de résultat"""
        if not result_str:
            return 0
        
        # Format typique: "4-0", "3-1", "2-2", etc.
        if "-" in result_str:
            try:
                wins_str = result_str.split("-")[0]
                return int(wins_str)
            except (ValueError, IndexError):
                pass
        
        return 0
    
    async def get_stats(self) -> CacheStats:
        """Récupérer les statistiques du cache"""
        if not self._cache_loaded:
            await self.initialize()
        
        return self._stats_cache
    
    async def search_tournaments(self, query: str, limit: int = 20) -> List[CachedTournament]:
        """
        Recherche textuelle dans les tournois
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des tournois correspondants
        """
        if not self._cache_loaded:
            await self.initialize()
        
        query_lower = query.lower()
        results = []
        
        for tournament in self._tournaments_cache.values():
            # Recherche dans le nom et la source
            if (query_lower in tournament.name.lower() or 
                query_lower in tournament.source.lower() or
                query_lower in tournament.format.lower()):
                results.append(tournament)
        
        # Trier par pertinence (date récente d'abord)
        results.sort(key=lambda t: t.date, reverse=True)
        
        return results[:limit]
    
    async def needs_update(self, max_age_hours: int = 24) -> bool:
        """
        Vérifier si le cache nécessite une mise à jour
        
        Args:
            max_age_hours: Âge maximum du cache en heures
            
        Returns:
            True si mise à jour nécessaire
        """
        if not self.last_sync_file.exists():
            return True
        
        try:
            last_sync_str = self.last_sync_file.read_text().strip()
            last_sync = datetime.fromisoformat(last_sync_str)
            age = datetime.now() - last_sync
            
            return age.total_seconds() > (max_age_hours * 3600)
            
        except Exception:
            return True
    
    async def force_refresh(self) -> bool:
        """
        Forcer la mise à jour complète du cache
        
        Returns:
            True si mise à jour réussie
        """
        self.logger.info("🔄 Forcing cache refresh...")
        
        try:
            await self._update_repository()
            await self._load_tournaments_cache()
            await self._compute_stats()
            
            self.logger.info("✅ Cache refresh completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cache refresh failed: {e}")
            return False
    
    async def get_format_meta_snapshot(self, 
                                     format_name: str, 
                                     days_back: int = 30) -> Dict[str, Any]:
        """
        Obtenir un snapshot du méta pour un format
        
        Args:
            format_name: Nom du format (Modern, Standard, etc.)
            days_back: Nombre de jours en arrière
            
        Returns:
            Dictionnaire avec analyse du méta
        """
        if not self._cache_loaded:
            await self.initialize()
        
        # Calculer la date limite
        date_limit = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Récupérer les decks du format
        decks = await self.get_decks(
            format_filter=format_name,
            limit=None
        )
        
        # Filtrer par date
        recent_decks = [
            deck for deck in decks 
            if deck.get("tournament_date", "") >= date_limit
        ]
        
        # Analyser les archétypes
        archetype_counts = {}
        total_decks = len(recent_decks)
        
        for deck in recent_decks:
            archetype = deck.get("Archetype", "Unknown")
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        
        # Calculer les pourcentages
        archetype_percentages = {
            archetype: (count / total_decks * 100) if total_decks > 0 else 0
            for archetype, count in archetype_counts.items()
        }
        
        # Trier par popularité
        sorted_archetypes = sorted(
            archetype_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "format": format_name,
            "period_days": days_back,
            "total_decks": total_decks,
            "unique_archetypes": len(archetype_counts),
            "archetype_breakdown": sorted_archetypes[:20],  # Top 20
            "last_updated": datetime.now().isoformat()
        }

# Instance globale
mtgo_cache = MTGOCacheManager() 