"""
Scraper unifié pour Metalyzr
Combine API Melee.gg, scraping MTGTop8, et classification d'archétypes
Le meilleur des deux mondes !
"""
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from config import config
from melee_api_client import MeleeAPIClient, fetch_melee_tournaments
from mtgtop8_scraper import MTGTop8Scraper
from archetype_classifier import default_classifier, ArchetypeMatch
from data_manager import DataManager
from mtgo_cache_manager import MTGOCacheManager, mtgo_cache

class UnifiedScraper:
    """
    Scraper unifié combinant toutes les sources et la classification
    """
    
    def __init__(self):
        self.logger = logging.getLogger("scraper.unified")
        self.data_manager = DataManager()
        
        # Priorités des sources (1 = plus haute priorité)
        self.source_priorities = {
            "melee.gg": 1,           # API officielle - priorité absolue
            "mtgo_cache": 2,         # Cache MTGODecklistCache - backbone données
            "mtgtop8": 3,            # Scraping - fallback fiable
            "mtgo": 4                # Future implémentation
        }
        
        # Gestionnaire cache MTGO
        self.mtgo_cache = mtgo_cache
        
    async def scrape_all_sources(self, 
                                format_name: str = "Modern",
                                max_tournaments_per_source: int = 10,
                                prefer_recent: bool = True) -> Dict[str, Any]:
        """
        Scraper toutes les sources disponibles pour un format
        
        Args:
            format_name: Format MTG à scraper
            max_tournaments_per_source: Limite par source
            prefer_recent: Prioriser les tournois récents
            
        Returns:
            Résumé des données collectées avec statistiques
        """
        self.logger.info(f"Starting unified scraping for format: {format_name}")
        
        start_time = datetime.now()
        results = {
            "format": format_name,
            "start_time": start_time,
            "sources": {},
            "total_tournaments": 0,
            "total_decks": 0,
            "archetypes_found": {},
            "errors": []
        }
        
        # 1. Priorité #1: API Melee.gg
        try:
            melee_results = await self._scrape_melee_source(format_name, max_tournaments_per_source)
            results["sources"]["melee.gg"] = melee_results
            results["total_tournaments"] += melee_results["tournament_count"]
            results["total_decks"] += melee_results["deck_count"]
            
        except Exception as e:
            error_msg = f"Melee.gg scraping failed: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
        
        # 2. Priorité #2: Cache MTGODecklistCache (backbone)
        try:
            cache_results = await self._scrape_mtgo_cache_source(format_name, max_tournaments_per_source)
            results["sources"]["mtgo_cache"] = cache_results
            results["total_tournaments"] += cache_results["tournament_count"]
            results["total_decks"] += cache_results["deck_count"]
            
        except Exception as e:
            error_msg = f"MTGODecklistCache scraping failed: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
        
        # 3. Priorité #3: Scraping MTGTop8 (fallback)
        try:
            mtgtop8_results = await self._scrape_mtgtop8_source(format_name, max_tournaments_per_source)
            results["sources"]["mtgtop8"] = mtgtop8_results
            results["total_tournaments"] += mtgtop8_results["tournament_count"]
            results["total_decks"] += mtgtop8_results["deck_count"]
            
        except Exception as e:
            error_msg = f"MTGTop8 scraping failed: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
        
        # 3. Analyser et classifier tous les decks collectés
        results["archetypes_found"] = await self._analyze_collected_data(format_name)
        
        # 4. Statistiques finales
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - start_time).total_seconds()
        
        self.logger.info(f"Unified scraping completed in {results['duration']:.2f}s")
        self.logger.info(f"Collected {results['total_tournaments']} tournaments, {results['total_decks']} decks")
        
        return results
    
    async def _scrape_melee_source(self, format_name: str, max_tournaments: int) -> Dict[str, Any]:
        """Scraper les données via l'API Melee.gg"""
        self.logger.info(f"Scraping Melee.gg API for {format_name}")
        
        source_result = {
            "source": "melee.gg",
            "method": "api", 
            "tournament_count": 0,
            "deck_count": 0,
            "tournaments": [],
            "errors": []
        }
        
        try:
            # Utiliser le client API Melee.gg
            tournaments = await fetch_melee_tournaments(format_name, max_tournaments)
            
            for tournament in tournaments:
                # Classifier les decks avec notre système
                classified_tournament = await self._classify_tournament_decks(tournament, format_name)
                
                # Sauvegarder en base
                tournament_id = self.data_manager.save_tournament_data(classified_tournament)
                if tournament_id:
                    source_result["tournaments"].append({
                        "id": tournament_id,
                        "name": classified_tournament["name"],
                        "deck_count": len(classified_tournament.get("decks", [])),
                        "source_url": classified_tournament.get("external_url")
                    })
                    source_result["deck_count"] += len(classified_tournament.get("decks", []))
            
            source_result["tournament_count"] = len(tournaments)
            self.logger.info(f"Melee.gg: {len(tournaments)} tournaments, {source_result['deck_count']} decks")
            
        except Exception as e:
            error_msg = f"Melee.gg API error: {str(e)}"
            source_result["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return source_result
    
    async def _scrape_mtgtop8_source(self, format_name: str, max_tournaments: int) -> Dict[str, Any]:
        """Scraper les données via MTGTop8 (scraping HTML)"""
        self.logger.info(f"Scraping MTGTop8 for {format_name}")
        
        source_result = {
            "source": "mtgtop8",
            "method": "scraping",
            "tournament_count": 0,
            "deck_count": 0,
            "tournaments": [],
            "errors": []
        }
        
        try:
            async with MTGTop8Scraper() as scraper:
                tournaments = await scraper.scrape_tournaments(format_name, max_tournaments)
                
                for tournament in tournaments:
                    # Classifier les decks
                    classified_tournament = await self._classify_tournament_decks(tournament, format_name)
                    
                    # Sauvegarder en base
                    tournament_id = self.data_manager.save_tournament_data(classified_tournament)
                    if tournament_id:
                        source_result["tournaments"].append({
                            "id": tournament_id,
                            "name": classified_tournament["name"],
                            "deck_count": len(classified_tournament.get("decks", [])),
                            "source_url": classified_tournament.get("source_url")
                        })
                        source_result["deck_count"] += len(classified_tournament.get("decks", []))
                
                source_result["tournament_count"] = len(tournaments)
                self.logger.info(f"MTGTop8: {len(tournaments)} tournaments, {source_result['deck_count']} decks")
                
        except Exception as e:
            error_msg = f"MTGTop8 scraping error: {str(e)}"
            source_result["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return source_result
    
    async def _scrape_mtgo_cache_source(self, format_name: str, max_tournaments: int) -> Dict[str, Any]:
        """Récupérer les données depuis MTGODecklistCache"""
        self.logger.info(f"Loading MTGODecklistCache data for {format_name}")
        
        source_result = {
            "source": "mtgo_cache",
            "method": "cache",
            "tournament_count": 0,
            "deck_count": 0,
            "tournaments": [],
            "errors": []
        }
        
        try:
            # Initialiser le cache si nécessaire
            if not self.mtgo_cache._cache_loaded:
                await self.mtgo_cache.initialize()
            
            # Récupérer les tournois récents du format
            tournaments = await self.mtgo_cache.get_tournaments(
                format_filter=format_name,
                limit=max_tournaments,
                include_archive=True
            )
            
            for tournament in tournaments:
                # Convertir en format unifié Metalyzr
                unified_tournament = {
                    "name": tournament.name,
                    "date": tournament.date,
                    "format": tournament.format,
                    "source": "mtgo_cache",
                    "external_url": tournament.url,
                    "decks": []
                }
                
                # Classifier les decks avec engine Badaro
                for deck_data in tournament.decks:
                    deck = {
                        "player": deck_data.get("Player", ""),
                        "position": deck_data.get("Result", ""),
                        "mainboard": deck_data.get("Mainboard", {}),
                        "sideboard": deck_data.get("Sideboard", {}),
                        "archetype": deck_data.get("Archetype", ""),  # Pré-classifié
                        "source": "mtgo_cache"
                    }
                    unified_tournament["decks"].append(deck)
                
                # Re-classifier avec notre engine pour harmoniser
                classified_tournament = await self._classify_tournament_decks(unified_tournament, format_name)
                
                # Sauvegarder en base
                tournament_id = self.data_manager.save_tournament_data(classified_tournament)
                if tournament_id:
                    source_result["tournaments"].append({
                        "id": tournament_id,
                        "name": classified_tournament["name"],
                        "deck_count": len(classified_tournament.get("decks", [])),
                        "source_url": classified_tournament.get("external_url")
                    })
                    source_result["deck_count"] += len(classified_tournament.get("decks", []))
            
            source_result["tournament_count"] = len(tournaments)
            self.logger.info(f"MTGOCache: {len(tournaments)} tournaments, {source_result['deck_count']} decks")
            
        except Exception as e:
            error_msg = f"MTGODecklistCache error: {str(e)}"
            source_result["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return source_result
    
    async def _classify_tournament_decks(self, tournament: Dict[str, Any], format_name: str) -> Dict[str, Any]:
        """
        Classifier tous les decks d'un tournoi avec notre système d'archétypes
        Inspiré de la logique MTGOArchetypeParser
        """
        classified_tournament = tournament.copy()
        classified_decks = []
        
        decks = tournament.get("decks", [])
        
        for deck in decks:
            classified_deck = deck.copy()
            
            # Extraire mainboard et sideboard
            mainboard = deck.get("mainboard", {})
            sideboard = deck.get("sideboard", {})
            
            # Classifier avec notre système
            archetype_match: ArchetypeMatch = default_classifier.classify_deck(
                mainboard=mainboard,
                sideboard=sideboard,
                format_name=format_name
            )
            
            # Enrichir le deck avec les données de classification
            classified_deck.update({
                "archetype": archetype_match.archetype_name,
                "archetype_confidence": archetype_match.confidence.value,
                "archetype_score": archetype_match.score,
                "archetype_details": {
                    "matched_rules": archetype_match.matched_rules,
                    "signature_cards": archetype_match.signature_cards_found,
                    "missing_cards": archetype_match.missing_cards
                }
            })
            
            classified_decks.append(classified_deck)
        
        classified_tournament["decks"] = classified_decks
        
        # Ajouter des statistiques d'archétypes au niveau tournoi
        archetype_stats = self._calculate_tournament_archetype_stats(classified_decks)
        classified_tournament["archetype_breakdown"] = archetype_stats
        
        return classified_tournament
    
    def _calculate_tournament_archetype_stats(self, decks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculer les statistiques d'archétypes pour un tournoi"""
        archetype_counts = {}
        confidence_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
        
        for deck in decks:
            archetype = deck.get("archetype", "Unknown")
            confidence = deck.get("archetype_confidence", "unknown")
            
            # Compter les archétypes
            if archetype in archetype_counts:
                archetype_counts[archetype] += 1
            else:
                archetype_counts[archetype] = 1
            
            # Compter les niveaux de confiance
            if confidence in confidence_counts:
                confidence_counts[confidence] += 1
        
        # Calculer les pourcentages
        total_decks = len(decks)
        if total_decks > 0:
            archetype_percentages = {
                arch: (count / total_decks) * 100 
                for arch, count in archetype_counts.items()
            }
        else:
            archetype_percentages = {}
        
        return {
            "total_decks": total_decks,
            "archetype_counts": archetype_counts,
            "archetype_percentages": archetype_percentages,
            "confidence_distribution": confidence_counts,
            "most_popular": max(archetype_counts.items(), key=lambda x: x[1])[0] if archetype_counts else "Unknown"
        }
    
    async def _analyze_collected_data(self, format_name: str) -> Dict[str, Any]:
        """Analyser toutes les données collectées pour un format"""
        try:
            # Récupérer les statistiques depuis le data manager
            format_stats = self.data_manager.get_format_statistics(format_name)
            
            return {
                "format": format_name,
                "analysis_date": datetime.now(),
                "total_tournaments_analyzed": format_stats.get("tournament_count", 0),
                "total_decks_analyzed": format_stats.get("deck_count", 0),
                "unique_archetypes": format_stats.get("unique_archetypes", []),
                "archetype_distribution": format_stats.get("archetype_breakdown", {}),
                "confidence_distribution": format_stats.get("confidence_stats", {}),
                "top_archetypes": format_stats.get("top_archetypes", [])
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing collected data: {str(e)}")
            return {"error": str(e)}
    
    async def scrape_format_priority(self, format_name: str, max_total: int = 50) -> Dict[str, Any]:
        """
        Scraper avec priorisation intelligente des sources
        Melee.gg d'abord, puis MTGTop8 pour compléter
        """
        self.logger.info(f"Priority scraping for {format_name} (max {max_total} tournaments)")
        
        # 70% Melee.gg, 30% MTGTop8 pour diversité
        melee_quota = int(max_total * 0.7)
        mtgtop8_quota = max_total - melee_quota
        
        return await self.scrape_all_sources(
            format_name=format_name,
            max_tournaments_per_source=melee_quota
        )

# Instance globale pour utilisation
unified_scraper = UnifiedScraper() 