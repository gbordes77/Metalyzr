"""
Intégration avec le moteur de classification d'archétypes de Badaro
Port Python du moteur C# Badaro/MTGOArchetypeParser
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ArchetypeCondition:
    """Condition pour la classification d'archétypes"""
    type: str  # InMainboard, InSideboard, OneOrMoreInMainboard, etc.
    cards: List[str]

@dataclass
class ArchetypeVariant:
    """Variante d'archétype"""
    name: str
    conditions: List[ArchetypeCondition]

@dataclass
class ArchetypeDefinition:
    """Définition d'archétype"""
    name: str
    include_color_in_name: bool = True
    conditions: List[ArchetypeCondition] = field(default_factory=list)
    variants: List[ArchetypeVariant] = field(default_factory=list)

@dataclass
class FallbackDefinition:
    """Définition de fallback pour archétypes generiques"""
    name: str
    common_cards: List[str]
    minimum_match_percentage: float = 0.1

@dataclass
class DeckCard:
    """Carte dans un deck"""
    name: str
    count: int
    location: str = "mainboard"  # mainboard, sideboard

class BadaroArchetypeEngine:
    """Moteur de classification d'archétypes basé sur Badaro/MTGOArchetypeParser"""
    
    def __init__(self, format_data_dir: str = "data/archetype_formats"):
        self.format_data_dir = Path(format_data_dir)
        self.format_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Types de conditions supportés
        self.condition_types = {
            "InMainboard": self._check_in_mainboard,
            "InSideboard": self._check_in_sideboard,
            "InMainOrSideboard": self._check_in_main_or_sideboard,
            "OneOrMoreInMainboard": self._check_one_or_more_in_mainboard,
            "OneOrMoreInSideboard": self._check_one_or_more_in_sideboard,
            "OneOrMoreInMainOrSideboard": self._check_one_or_more_in_main_or_sideboard,
            "TwoOrMoreInMainboard": self._check_two_or_more_in_mainboard,
            "TwoOrMoreInSideboard": self._check_two_or_more_in_sideboard,
            "TwoOrMoreInMainOrSideboard": self._check_two_or_more_in_main_or_sideboard,
            "DoesNotContain": self._check_does_not_contain,
            "DoesNotContainMainboard": self._check_does_not_contain_mainboard,
            "DoesNotContainSideboard": self._check_does_not_contain_sideboard
        }
        
        # Cache des formats chargés
        self.loaded_formats = {}
    
    def _load_format_data(self, format_name: str) -> Dict[str, Any]:
        """Charger les données d'un format"""
        if format_name in self.loaded_formats:
            return self.loaded_formats[format_name]
        
        format_dir = self.format_data_dir / format_name
        if not format_dir.exists():
            logger.warning(f"Format directory not found: {format_dir}")
            return {"archetypes": [], "fallbacks": []}
        
        # Charger les archétypes
        archetypes = []
        archetypes_dir = format_dir / "archetypes"
        if archetypes_dir.exists():
            for archetype_file in archetypes_dir.glob("*.json"):
                try:
                    with open(archetype_file, 'r', encoding='utf-8') as f:
                        archetype_data = json.load(f)
                        archetypes.append(self._parse_archetype_definition(archetype_data))
                except Exception as e:
                    logger.error(f"Error loading archetype {archetype_file}: {e}")
        
        # Charger les fallbacks
        fallbacks = []
        fallbacks_dir = format_dir / "fallbacks"
        if fallbacks_dir.exists():
            for fallback_file in fallbacks_dir.glob("*.json"):
                try:
                    with open(fallback_file, 'r', encoding='utf-8') as f:
                        fallback_data = json.load(f)
                        fallbacks.append(self._parse_fallback_definition(fallback_data))
                except Exception as e:
                    logger.error(f"Error loading fallback {fallback_file}: {e}")
        
        format_data = {
            "archetypes": archetypes,
            "fallbacks": fallbacks
        }
        
        self.loaded_formats[format_name] = format_data
        return format_data
    
    def _parse_archetype_definition(self, data: Dict) -> ArchetypeDefinition:
        """Parser une définition d'archétype depuis JSON"""
        conditions = []
        for condition_data in data.get("conditions", []):
            conditions.append(ArchetypeCondition(
                type=condition_data["type"],
                cards=condition_data["cards"]
            ))
        
        variants = []
        for variant_data in data.get("variants", []):
            variant_conditions = []
            for condition_data in variant_data.get("conditions", []):
                variant_conditions.append(ArchetypeCondition(
                    type=condition_data["type"],
                    cards=condition_data["cards"]
                ))
            
            variants.append(ArchetypeVariant(
                name=variant_data["name"],
                conditions=variant_conditions
            ))
        
        return ArchetypeDefinition(
            name=data["name"],
            include_color_in_name=data.get("include_color_in_name", True),
            conditions=conditions,
            variants=variants
        )
    
    def _parse_fallback_definition(self, data: Dict) -> FallbackDefinition:
        """Parser une définition de fallback depuis JSON"""
        return FallbackDefinition(
            name=data["name"],
            common_cards=data.get("common_cards", []),
            minimum_match_percentage=data.get("minimum_match_percentage", 0.1)
        )
    
    def _get_deck_cards(self, deck_data: Dict) -> List[DeckCard]:
        """Extraire les cartes d'un deck"""
        cards = []
        
        # Mainboard
        for card in deck_data.get("mainboard", []):
            cards.append(DeckCard(
                name=card["name"],
                count=card.get("count", 1),
                location="mainboard"
            ))
        
        # Sideboard
        for card in deck_data.get("sideboard", []):
            cards.append(DeckCard(
                name=card["name"],
                count=card.get("count", 1),
                location="sideboard"
            ))
        
        return cards
    
    def _check_in_mainboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si toutes les cartes sont dans le mainboard"""
        mainboard_cards = {card.name for card in cards if card.location == "mainboard"}
        return all(card in mainboard_cards for card in target_cards)
    
    def _check_in_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si toutes les cartes sont dans le sideboard"""
        sideboard_cards = {card.name for card in cards if card.location == "sideboard"}
        return all(card in sideboard_cards for card in target_cards)
    
    def _check_in_main_or_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si toutes les cartes sont dans le mainboard ou sideboard"""
        all_cards = {card.name for card in cards}
        return all(card in all_cards for card in target_cards)
    
    def _check_one_or_more_in_mainboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins une carte est dans le mainboard"""
        mainboard_cards = {card.name for card in cards if card.location == "mainboard"}
        return any(card in mainboard_cards for card in target_cards)
    
    def _check_one_or_more_in_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins une carte est dans le sideboard"""
        sideboard_cards = {card.name for card in cards if card.location == "sideboard"}
        return any(card in sideboard_cards for card in target_cards)
    
    def _check_one_or_more_in_main_or_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins une carte est dans le mainboard ou sideboard"""
        all_cards = {card.name for card in cards}
        return any(card in all_cards for card in target_cards)
    
    def _check_two_or_more_in_mainboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins deux cartes sont dans le mainboard"""
        mainboard_cards = {card.name for card in cards if card.location == "mainboard"}
        matches = sum(1 for card in target_cards if card in mainboard_cards)
        return matches >= 2
    
    def _check_two_or_more_in_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins deux cartes sont dans le sideboard"""
        sideboard_cards = {card.name for card in cards if card.location == "sideboard"}
        matches = sum(1 for card in target_cards if card in sideboard_cards)
        return matches >= 2
    
    def _check_two_or_more_in_main_or_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier si au moins deux cartes sont dans le mainboard ou sideboard"""
        all_cards = {card.name for card in cards}
        matches = sum(1 for card in target_cards if card in all_cards)
        return matches >= 2
    
    def _check_does_not_contain(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier qu'aucune carte n'est présente"""
        all_cards = {card.name for card in cards}
        return not any(card in all_cards for card in target_cards)
    
    def _check_does_not_contain_mainboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier qu'aucune carte n'est présente dans le mainboard"""
        mainboard_cards = {card.name for card in cards if card.location == "mainboard"}
        return not any(card in mainboard_cards for card in target_cards)
    
    def _check_does_not_contain_sideboard(self, cards: List[DeckCard], target_cards: List[str]) -> bool:
        """Vérifier qu'aucune carte n'est présente dans le sideboard"""
        sideboard_cards = {card.name for card in cards if card.location == "sideboard"}
        return not any(card in sideboard_cards for card in target_cards)
    
    def _check_condition(self, condition: ArchetypeCondition, cards: List[DeckCard]) -> bool:
        """Vérifier une condition d'archétype"""
        check_func = self.condition_types.get(condition.type)
        if not check_func:
            logger.warning(f"Unknown condition type: {condition.type}")
            return False
        
        return check_func(cards, condition.cards)
    
    def _check_archetype_match(self, archetype: ArchetypeDefinition, cards: List[DeckCard]) -> bool:
        """Vérifier si un deck correspond à un archétype"""
        # Toutes les conditions doivent être satisfaites
        for condition in archetype.conditions:
            if not self._check_condition(condition, cards):
                return False
        
        return True
    
    def _check_variant_match(self, variant: ArchetypeVariant, cards: List[DeckCard]) -> bool:
        """Vérifier si un deck correspond à une variante"""
        # Toutes les conditions doivent être satisfaites
        for condition in variant.conditions:
            if not self._check_condition(condition, cards):
                return False
        
        return True
    
    def _check_fallback_match(self, fallback: FallbackDefinition, cards: List[DeckCard]) -> float:
        """Calculer le score de correspondance avec un fallback"""
        all_cards = {card.name for card in cards}
        matching_cards = sum(1 for card in fallback.common_cards if card in all_cards)
        
        if len(fallback.common_cards) == 0:
            return 0.0
        
        return matching_cards / len(fallback.common_cards)
    
    def _get_deck_colors(self, cards: List[DeckCard]) -> str:
        """Déterminer les couleurs d'un deck (version simplifiée)"""
        # Implémentation simplifiée basée sur les noms de cartes
        color_indicators = {
            "W": ["Plains", "White", "Swords to Plowshares"],
            "U": ["Island", "Blue", "Counterspell"],
            "B": ["Swamp", "Black", "Dark Ritual"],
            "R": ["Mountain", "Red", "Lightning Bolt"],
            "G": ["Forest", "Green", "Giant Growth"]
        }
        
        detected_colors = set()
        card_names = {card.name for card in cards}
        
        for color, indicators in color_indicators.items():
            if any(indicator in card_names for indicator in indicators):
                detected_colors.add(color)
        
        # Trier les couleurs selon l'ordre WUBRG
        color_order = "WUBRG"
        return "".join(color for color in color_order if color in detected_colors)
    
    def classify_deck(self, deck_data: Dict, format_name: str) -> Dict[str, Any]:
        """Classifier un deck selon son archétype"""
        format_data = self._load_format_data(format_name)
        cards = self._get_deck_cards(deck_data)
        
        # Vérifier les archétypes
        for archetype in format_data["archetypes"]:
            if self._check_archetype_match(archetype, cards):
                # Vérifier les variantes
                for variant in archetype.variants:
                    if self._check_variant_match(variant, cards):
                        archetype_name = f"{archetype.name} - {variant.name}"
                        if archetype.include_color_in_name:
                            colors = self._get_deck_colors(cards)
                            if colors:
                                archetype_name = f"{colors} {archetype_name}"
                        
                        return {
                            "archetype": archetype_name,
                            "base_archetype": archetype.name,
                            "variant": variant.name,
                            "colors": self._get_deck_colors(cards),
                            "classification_type": "archetype",
                            "confidence": 1.0
                        }
                
                # Archétype principal sans variante
                archetype_name = archetype.name
                if archetype.include_color_in_name:
                    colors = self._get_deck_colors(cards)
                    if colors:
                        archetype_name = f"{colors} {archetype_name}"
                
                return {
                    "archetype": archetype_name,
                    "base_archetype": archetype.name,
                    "variant": None,
                    "colors": self._get_deck_colors(cards),
                    "classification_type": "archetype",
                    "confidence": 1.0
                }
        
        # Vérifier les fallbacks
        best_fallback = None
        best_score = 0.0
        
        for fallback in format_data["fallbacks"]:
            score = self._check_fallback_match(fallback, cards)
            if score > best_score and score >= fallback.minimum_match_percentage:
                best_score = score
                best_fallback = fallback
        
        if best_fallback:
            fallback_name = best_fallback.name
            colors = self._get_deck_colors(cards)
            if colors:
                fallback_name = f"{colors} {fallback_name}"
            
            return {
                "archetype": fallback_name,
                "base_archetype": best_fallback.name,
                "variant": None,
                "colors": colors,
                "classification_type": "fallback",
                "confidence": best_score
            }
        
        # Aucune correspondance trouvée
        colors = self._get_deck_colors(cards)
        fallback_name = f"{colors} Unknown" if colors else "Unknown"
        
        return {
            "archetype": fallback_name,
            "base_archetype": "Unknown",
            "variant": None,
            "colors": colors,
            "classification_type": "unknown",
            "confidence": 0.0
        }
    
    def create_archetype_definition(self, archetype_data: Dict) -> ArchetypeDefinition:
        """Créer une définition d'archétype"""
        return self._parse_archetype_definition(archetype_data)
    
    def save_archetype_definition(self, archetype: ArchetypeDefinition, format_name: str):
        """Sauvegarder une définition d'archétype"""
        format_dir = self.format_data_dir / format_name
        archetypes_dir = format_dir / "archetypes"
        archetypes_dir.mkdir(parents=True, exist_ok=True)
        
        # Serialiser en JSON
        archetype_data = {
            "name": archetype.name,
            "include_color_in_name": archetype.include_color_in_name,
            "conditions": [
                {
                    "type": condition.type,
                    "cards": condition.cards
                }
                for condition in archetype.conditions
            ],
            "variants": [
                {
                    "name": variant.name,
                    "conditions": [
                        {
                            "type": condition.type,
                            "cards": condition.cards
                        }
                        for condition in variant.conditions
                    ]
                }
                for variant in archetype.variants
            ]
        }
        
        # Sauvegarder
        archetype_file = archetypes_dir / f"{archetype.name.lower().replace(' ', '_')}.json"
        with open(archetype_file, 'w', encoding='utf-8') as f:
            json.dump(archetype_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved archetype definition: {archetype.name}")
    
    def get_format_statistics(self, format_name: str) -> Dict[str, Any]:
        """Obtenir les statistiques d'un format"""
        format_data = self._load_format_data(format_name)
        
        return {
            "archetypes_count": len(format_data["archetypes"]),
            "fallbacks_count": len(format_data["fallbacks"]),
            "archetype_names": [archetype.name for archetype in format_data["archetypes"]],
            "fallback_names": [fallback.name for fallback in format_data["fallbacks"]]
        }
    
    def get_supported_formats(self) -> List[str]:
        """Obtenir la liste des formats supportés"""
        formats = []
        for format_dir in self.format_data_dir.iterdir():
            if format_dir.is_dir():
                formats.append(format_dir.name)
        return formats 