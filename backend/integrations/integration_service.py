"""
Service principal d'intégration qui combine les 3 moteurs :
- Jiliac Cache
- MTG Scraper
- Badaro Archetype Engine
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .jiliac_cache import JiliacCacheClient
from .mtg_scraper import MTGScraper
from .badaro_archetype_engine import BadaroArchetypeEngine

logger = logging.getLogger(__name__)

class IntegrationService:
    """Service principal d'intégration des 3 moteurs"""
    
    def __init__(self, cache_dir: str = "cache/integrations"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialiser les 3 moteurs
        self.jiliac_cache = JiliacCacheClient(str(self.cache_dir / "jiliac"))
        self.mtg_scraper = MTGScraper(str(self.cache_dir / "scraper"))
        self.badaro_engine = BadaroArchetypeEngine(str(self.cache_dir / "archetype_formats"))
        
        logger.info("IntegrationService initialized with real 3 engines")
    
    def get_recent_tournaments_with_archetypes(self, 
                                              days: int = 7, 
                                              format_name: str = "Modern") -> List[Dict]:
        """Obtenir les tournois récents avec classification d'archétypes"""
        logger.info(f"Fetching recent tournaments for {format_name} ({days} days)")
        
        # 1. Obtenir les tournois depuis le cache Jiliac
        tournaments = self.jiliac_cache.get_recent_tournaments(days)
        
        # 2. Classifier les archétypes avec Badaro
        enhanced_tournaments = []
        for tournament in tournaments:
            tournament_info = tournament.get("tournament", {})
            if tournament_info.get("format", "").lower() != format_name.lower():
                continue
            
            enhanced_decks = []
            for deck in tournament.get("decks", []):
                # Classifier l'archétype
                classification = self.badaro_engine.classify_deck(deck, format_name)
                
                # Ajouter les infos de classification
                enhanced_deck = {
                    **deck,
                    "archetype_classification": classification
                }
                enhanced_decks.append(enhanced_deck)
            
            enhanced_tournament = {
                **tournament,
                "decks": enhanced_decks
            }
            enhanced_tournaments.append(enhanced_tournament)
        
        logger.info(f"Enhanced {len(enhanced_tournaments)} tournaments with archetype classification")
        return enhanced_tournaments
    
    def scrape_and_classify_deck(self, url: str, format_name: str = "Modern") -> Optional[Dict]:
        """Scraper un deck et le classifier"""
        logger.info(f"Scraping and classifying deck from {url}")
        
        # 1. Scraper le deck
        deck_data = self.mtg_scraper.scrape_deck(url)
        if not deck_data:
            logger.error(f"Failed to scrape deck from {url}")
            return None
        
        # 2. Classifier l'archétype
        classification = self.badaro_engine.classify_deck(deck_data, format_name)
        
        # 3. Combiner les données
        result = {
            **deck_data,
            "format": format_name,
            "archetype_classification": classification,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed deck: {classification['archetype']}")
        return result
    
    def scrape_multiple_decks_and_classify(self, 
                                         urls: List[str], 
                                         format_name: str = "Modern") -> List[Dict]:
        """Scraper plusieurs decks et les classifier"""
        logger.info(f"Scraping and classifying {len(urls)} decks")
        
        results = []
        for url in urls:
            deck_data = self.scrape_and_classify_deck(url, format_name)
            if deck_data:
                results.append(deck_data)
        
        logger.info(f"Successfully processed {len(results)} decks")
        return results
    
    def get_meta_analysis(self, format_name: str = "Modern", days: int = 7) -> Dict[str, Any]:
        """Obtenir une analyse du méta"""
        logger.info(f"Performing meta analysis for {format_name}")
        
        # Obtenir les tournois récents avec archétypes
        tournaments = self.get_recent_tournaments_with_archetypes(days, format_name)
        
        # Analyser les archétypes
        archetype_counts = {}
        total_decks = 0
        
        for tournament in tournaments:
            for deck in tournament.get("decks", []):
                classification = deck.get("archetype_classification", {})
                archetype = classification.get("archetype", "Unknown")
                
                if archetype not in archetype_counts:
                    archetype_counts[archetype] = {
                        "count": 0,
                        "wins": 0,
                        "base_archetype": classification.get("base_archetype", "Unknown"),
                        "colors": classification.get("colors", ""),
                        "confidence": classification.get("confidence", 0.0)
                    }
                
                archetype_counts[archetype]["count"] += 1
                total_decks += 1
                
                # Compter les victoires (approximation)
                if "winner" in deck.get("player", "").lower():
                    archetype_counts[archetype]["wins"] += 1
        
        # Calculer les statistiques
        meta_stats = {
            "format": format_name,
            "analysis_period_days": days,
            "total_decks": total_decks,
            "total_tournaments": len(tournaments),
            "archetypes": {},
            "top_archetypes": [],
            "diversity_index": 0.0,
            "generated_at": datetime.now().isoformat()
        }
        
        # Calculer les pourcentages et taux de victoire
        for archetype, stats in archetype_counts.items():
            win_rate = (stats["wins"] / stats["count"]) if stats["count"] > 0 else 0.0
            percentage = (stats["count"] / total_decks * 100) if total_decks > 0 else 0.0
            
            meta_stats["archetypes"][archetype] = {
                "count": stats["count"],
                "percentage": percentage,
                "wins": stats["wins"],
                "win_rate": win_rate,
                "base_archetype": stats["base_archetype"],
                "colors": stats["colors"],
                "confidence": stats["confidence"]
            }
        
        # Top archétypes par popularité
        sorted_archetypes = sorted(
            meta_stats["archetypes"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        meta_stats["top_archetypes"] = [
            {
                "archetype": archetype,
                **stats
            }
            for archetype, stats in sorted_archetypes[:10]
        ]
        
        # Index de diversité (Shannon)
        if total_decks > 0:
            diversity = 0.0
            for stats in archetype_counts.values():
                p = stats["count"] / total_decks
                if p > 0:
                    diversity -= p * (p ** 0.5)  # Simplifié
            meta_stats["diversity_index"] = diversity
        
        logger.info(f"Meta analysis complete: {len(meta_stats['archetypes'])} archetypes")
        return meta_stats
    
    def search_tournaments_by_archetype(self, 
                                      archetype: str, 
                                      format_name: str = "Modern") -> List[Dict]:
        """Rechercher des tournois par archétype"""
        logger.info(f"Searching tournaments for archetype: {archetype}")
        
        # Obtenir tous les tournois en cache
        tournaments = self.jiliac_cache.search_tournaments(format_name)
        
        # Filtrer par archétype
        matching_tournaments = []
        for tournament in tournaments:
            enhanced_decks = []
            for deck in tournament.get("decks", []):
                # Classifier l'archétype
                classification = self.badaro_engine.classify_deck(deck, format_name)
                
                # Vérifier si ça correspond
                if archetype.lower() in classification.get("archetype", "").lower():
                    enhanced_deck = {
                        **deck,
                        "archetype_classification": classification
                    }
                    enhanced_decks.append(enhanced_deck)
            
            if enhanced_decks:
                matching_tournaments.append({
                    **tournament,
                    "decks": enhanced_decks
                })
        
        logger.info(f"Found {len(matching_tournaments)} tournaments with {archetype}")
        return matching_tournaments
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtenir le statut des intégrations"""
        return {
            "jiliac_cache": {
                "status": "active",
                "supported_sources": ["melee", "mtgo", "topdeck"],
                "cache_dir": str(self.jiliac_cache.cache_dir)
            },
            "mtg_scraper": {
                "status": "active",
                "supported_sites": self.mtg_scraper.get_supported_sites(),
                "cache_dir": str(self.mtg_scraper.cache_dir)
            },
            "badaro_engine": {
                "status": "active",
                "supported_formats": self.badaro_engine.get_supported_formats(),
                "data_dir": str(self.badaro_engine.format_data_dir)
            },
            "integration_service": {
                "status": "active",
                "features": [
                    "Recent tournaments with archetype classification",
                    "Deck scraping and classification",
                    "Meta analysis",
                    "Tournament search by archetype"
                ]
            }
        }
    
    def create_sample_archetype_data(self, format_name: str = "Modern"):
        """Créer des données d'archétype exemple"""
        logger.info(f"Creating sample archetype data for {format_name}")
        
        # Archétype Burn
        burn_archetype = {
            "name": "Burn",
            "include_color_in_name": True,
            "conditions": [
                {
                    "type": "InMainboard",
                    "cards": ["Lightning Bolt"]
                },
                {
                    "type": "OneOrMoreInMainboard",
                    "cards": ["Monastery Swiftspear", "Goblin Guide", "Eidolon of the Great Revel"]
                }
            ],
            "variants": []
        }
        
        # Archétype Control
        control_archetype = {
            "name": "Control",
            "include_color_in_name": True,
            "conditions": [
                {
                    "type": "OneOrMoreInMainboard",
                    "cards": ["Counterspell", "Mana Leak", "Cryptic Command"]
                },
                {
                    "type": "OneOrMoreInMainboard",
                    "cards": ["Wrath of God", "Supreme Verdict", "Damnation"]
                }
            ],
            "variants": []
        }
        
        # Sauvegarder les archétypes
        burn_def = self.badaro_engine.create_archetype_definition(burn_archetype)
        control_def = self.badaro_engine.create_archetype_definition(control_archetype)
        
        self.badaro_engine.save_archetype_definition(burn_def, format_name)
        self.badaro_engine.save_archetype_definition(control_def, format_name)
        
        # Créer des fallbacks
        fallbacks_dir = self.badaro_engine.format_data_dir / format_name / "fallbacks"
        fallbacks_dir.mkdir(parents=True, exist_ok=True)
        
        # Fallback Midrange
        midrange_fallback = {
            "name": "Midrange",
            "common_cards": [
                "Tarmogoyf", "Dark Confidant", "Liliana of the Veil",
                "Thoughtseize", "Inquisition of Kozilek", "Lightning Bolt",
                "Path to Exile", "Fatal Push"
            ],
            "minimum_match_percentage": 0.2
        }
        
        with open(fallbacks_dir / "midrange.json", 'w', encoding='utf-8') as f:
            json.dump(midrange_fallback, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created sample archetype data for {format_name}")
    
    def close(self):
        """Fermer tous les clients"""
        self.jiliac_cache.close()
        self.mtg_scraper.close()
        logger.info("IntegrationService closed") 