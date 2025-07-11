"""
Engine d'archétypes inspiré directement de MTGOArchetypeParser (Badaro)
Implémentation Python des règles de production MTGO
"""
import json
import logging
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import requests
from pathlib import Path
import os

class ConditionType(Enum):
    """Types de conditions Badaro"""
    IN_MAINBOARD = "InMainboard"
    IN_SIDEBOARD = "InSideboard" 
    IN_MAIN_OR_SIDEBOARD = "InMainOrSideboard"
    ONE_OR_MORE_IN_MAINBOARD = "OneOrMoreInMainboard"
    ONE_OR_MORE_IN_SIDEBOARD = "OneOrMoreInSideboard"
    ONE_OR_MORE_IN_MAIN_OR_SIDEBOARD = "OneOrMoreInMainOrSideboard"
    TWO_OR_MORE_IN_MAINBOARD = "TwoOrMoreInMainboard"
    TWO_OR_MORE_IN_SIDEBOARD = "TwoOrMoreInSideboard"
    TWO_OR_MORE_IN_MAIN_OR_SIDEBOARD = "TwoOrMoreInMainOrSideboard"
    DOES_NOT_CONTAIN = "DoesNotContain"
    DOES_NOT_CONTAIN_MAINBOARD = "DoesNotContainMainboard"
    DOES_NOT_CONTAIN_SIDEBOARD = "DoesNotContainSideboard"

@dataclass
class ArchetypeCondition:
    """Condition Badaro pour détecter un archétype"""
    type: ConditionType
    cards: List[str]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ArchetypeCondition':
        return cls(
            type=ConditionType(data["Type"]),
            cards=data["Cards"]
        )

@dataclass  
class ArchetypeVariant:
    """Variante d'archétype (ex: UW Control vs Esper Control)"""
    name: str
    conditions: List[ArchetypeCondition]
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'ArchetypeVariant':
        conditions = [
            ArchetypeCondition.from_dict(cond) 
            for cond in data.get("Conditions", [])
        ]
        return cls(name=name, conditions=conditions)

@dataclass
class ArchetypeDefinition:
    """Définition complète d'un archétype selon Badaro"""
    name: str
    include_color_in_name: bool
    conditions: List[ArchetypeCondition]
    variants: List[ArchetypeVariant] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'ArchetypeDefinition':
        conditions = [
            ArchetypeCondition.from_dict(cond) 
            for cond in data.get("Conditions", [])
        ]
        
        variants = []
        for variant_name, variant_data in data.get("Variants", {}).items():
            variants.append(ArchetypeVariant.from_dict(variant_name, variant_data))
        
        return cls(
            name=name,
            include_color_in_name=data.get("IncludeColorInName", False),
            conditions=conditions,
            variants=variants
        )

@dataclass
class FallbackDefinition:
    """Définition Fallback pour decks 'goodstuff'"""
    name: str
    include_color_in_name: bool
    common_cards: List[str]
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'FallbackDefinition':
        return cls(
            name=name,
            include_color_in_name=data.get("IncludeColorInName", True),
            common_cards=data.get("CommonCards", [])
        )

@dataclass
class BadaroClassificationResult:
    """Résultat de classification selon Badaro"""
    archetype_name: str
    variant_name: Optional[str] = None
    confidence_score: float = 0.0
    matched_conditions: List[str] = field(default_factory=list)
    is_fallback: bool = False
    fallback_match_count: int = 0
    color_identity: str = ""

class BadaroArchetypeEngine:
    """
    Engine d'archétypes basé sur la logique exacte de MTGOArchetypeParser
    Utilise les vraies définitions Badaro depuis GitHub
    """
    
    def __init__(self, cache_dir: str = "./archetype_cache"):
        self.logger = logging.getLogger("badaro.archetype_engine")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # URLs des données Badaro
        self.badaro_base_url = "https://raw.githubusercontent.com/Badaro/MTGOFormatData/main/Formats"
        
        # Cache des définitions par format
        self.format_definitions: Dict[str, Dict[str, ArchetypeDefinition]] = {}
        self.format_fallbacks: Dict[str, Dict[str, FallbackDefinition]] = {}
        self.color_overrides: Dict[str, Dict[str, str]] = {}
        
    async def load_format_definitions(self, format_name: str, force_refresh: bool = False) -> bool:
        """
        Charger les définitions d'archétypes pour un format depuis GitHub Badaro
        
        Args:
            format_name: Format MTG (Modern, Standard, etc.)
            force_refresh: Forcer le rechargement depuis GitHub
            
        Returns:
            True si chargement réussi
        """
        try:
            cache_file = self.cache_dir / f"{format_name.lower()}_definitions.json"
            
            # Utiliser le cache si disponible et pas de refresh forcé
            if cache_file.exists() and not force_refresh:
                self.logger.info(f"Loading {format_name} definitions from cache")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    self._parse_format_data(format_name, cached_data)
                    return True
            
            # Télécharger depuis GitHub Badaro
            self.logger.info(f"Downloading {format_name} definitions from Badaro GitHub")
            
            # URLs des fichiers Badaro
            urls = {
                "archetypes": f"{self.badaro_base_url}/{format_name}/Archetypes",
                "fallbacks": f"{self.badaro_base_url}/{format_name}/Fallbacks", 
                "color_overrides": f"{self.badaro_base_url}/{format_name}/color_overrides.json"
            }
            
            format_data = {"archetypes": {}, "fallbacks": {}, "color_overrides": {}}
            
            # Charger les archétypes
            archetypes_data = await self._fetch_directory_files(urls["archetypes"])
            format_data["archetypes"] = archetypes_data
            
            # Charger les fallbacks
            fallbacks_data = await self._fetch_directory_files(urls["fallbacks"])
            format_data["fallbacks"] = fallbacks_data
            
            # Charger les overrides de couleurs
            try:
                color_response = requests.get(urls["color_overrides"], timeout=10)
                if color_response.status_code == 200:
                    format_data["color_overrides"] = color_response.json()
            except Exception as e:
                self.logger.warning(f"Could not load color overrides: {e}")
            
            # Sauvegarder en cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(format_data, f, indent=2, ensure_ascii=False)
            
            # Parser les données
            self._parse_format_data(format_name, format_data)
            
            self.logger.info(f"Loaded {len(self.format_definitions[format_name])} archetypes and {len(self.format_fallbacks[format_name])} fallbacks for {format_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load {format_name} definitions: {e}")
            return False
    
    async def _fetch_directory_files(self, base_url: str) -> Dict[str, Any]:
        """Récupérer tous les fichiers JSON d'un répertoire GitHub"""
        try:
            # Utiliser l'API GitHub pour lister les fichiers
            api_url = base_url.replace("raw.githubusercontent.com", "api.github.com/repos").replace("/main/", "/contents/")
            
            response = requests.get(api_url, timeout=10)
            if response.status_code != 200:
                return {}
            
            files_data = {}
            files_list = response.json()
            
            for file_info in files_list:
                if file_info["type"] == "file" and file_info["name"].endswith(".json"):
                    file_url = file_info["download_url"]
                    file_response = requests.get(file_url, timeout=10)
                    
                    if file_response.status_code == 200:
                        file_name = file_info["name"].replace(".json", "")
                        files_data[file_name] = file_response.json()
            
            return files_data
            
        except Exception as e:
            self.logger.error(f"Error fetching directory {base_url}: {e}")
            return {}
    
    def _parse_format_data(self, format_name: str, data: Dict[str, Any]):
        """Parser les données de format depuis Badaro"""
        
        # Parser les archétypes
        archetypes = {}
        for archetype_name, archetype_data in data.get("archetypes", {}).items():
            archetypes[archetype_name] = ArchetypeDefinition.from_dict(archetype_name, archetype_data)
        
        # Parser les fallbacks
        fallbacks = {}
        for fallback_name, fallback_data in data.get("fallbacks", {}).items():
            fallbacks[fallback_name] = FallbackDefinition.from_dict(fallback_name, fallback_data)
        
        # Stocker
        self.format_definitions[format_name] = archetypes
        self.format_fallbacks[format_name] = fallbacks
        self.color_overrides[format_name] = data.get("color_overrides", {})
    
    def classify_deck(self, 
                     mainboard: Dict[str, int], 
                     sideboard: Dict[str, int] = None,
                     format_name: str = "Modern") -> BadaroClassificationResult:
        """
        Classifier un deck selon la logique exacte Badaro
        
        Args:
            mainboard: Cartes du mainboard {nom: quantité}
            sideboard: Cartes du sideboard {nom: quantité}
            format_name: Format du deck
            
        Returns:
            BadaroClassificationResult avec classification complète
        """
        if sideboard is None:
            sideboard = {}
        
        # Vérifier que les définitions sont chargées
        if format_name not in self.format_definitions:
            self.logger.warning(f"No definitions loaded for format {format_name}")
            return self._unknown_classification()
        
        # Créer les ensembles de cartes
        mainboard_cards = set(mainboard.keys())
        sideboard_cards = set(sideboard.keys())
        all_cards = mainboard_cards | sideboard_cards
        
        # Phase 1: Essayer les archétypes exacts
        archetype_result = self._match_archetypes(
            mainboard, sideboard, mainboard_cards, sideboard_cards, all_cards, format_name
        )
        
        if archetype_result:
            return archetype_result
        
        # Phase 2: Essayer les fallbacks (goodstuff)
        fallback_result = self._match_fallbacks(
            all_cards, format_name
        )
        
        if fallback_result:
            return fallback_result
        
        # Phase 3: Classification par couleur en dernier recours
        return self._color_classification(mainboard_cards | sideboard_cards)
    
    def _match_archetypes(self, 
                         mainboard: Dict[str, int],
                         sideboard: Dict[str, int], 
                         mainboard_cards: Set[str],
                         sideboard_cards: Set[str],
                         all_cards: Set[str],
                         format_name: str) -> Optional[BadaroClassificationResult]:
        """Phase 1: Matcher contre les archétypes définis"""
        
        archetypes = self.format_definitions[format_name]
        
        for archetype_name, archetype_def in archetypes.items():
            # Tester l'archétype principal
            if self._evaluate_conditions(archetype_def.conditions, mainboard, sideboard, mainboard_cards, sideboard_cards, all_cards):
                
                # Tester les variantes
                best_variant = None
                for variant in archetype_def.variants:
                    if self._evaluate_conditions(variant.conditions, mainboard, sideboard, mainboard_cards, sideboard_cards, all_cards):
                        best_variant = variant.name
                        break
                
                # Calculer la couleur si nécessaire
                color_identity = ""
                if archetype_def.include_color_in_name:
                    color_identity = self._extract_color_identity(all_cards, format_name)
                
                return BadaroClassificationResult(
                    archetype_name=archetype_name,
                    variant_name=best_variant,
                    confidence_score=95.0,  # Haute confiance pour les matches exacts
                    matched_conditions=[f"Archetype: {archetype_name}"],
                    color_identity=color_identity
                )
        
        return None
    
    def _evaluate_conditions(self,
                           conditions: List[ArchetypeCondition],
                           mainboard: Dict[str, int],
                           sideboard: Dict[str, int],
                           mainboard_cards: Set[str],
                           sideboard_cards: Set[str], 
                           all_cards: Set[str]) -> bool:
        """Évaluer si toutes les conditions sont satisfaites"""
        
        for condition in conditions:
            if not self._evaluate_single_condition(condition, mainboard, sideboard, mainboard_cards, sideboard_cards, all_cards):
                return False
        
        return True
    
    def _evaluate_single_condition(self,
                                 condition: ArchetypeCondition,
                                 mainboard: Dict[str, int],
                                 sideboard: Dict[str, int],
                                 mainboard_cards: Set[str],
                                 sideboard_cards: Set[str],
                                 all_cards: Set[str]) -> bool:
        """Évaluer une condition individuelle selon la logique Badaro"""
        
        condition_type = condition.type
        required_cards = set(condition.cards)
        
        if condition_type == ConditionType.IN_MAINBOARD:
            return required_cards.issubset(mainboard_cards)
        
        elif condition_type == ConditionType.IN_SIDEBOARD:
            return required_cards.issubset(sideboard_cards)
        
        elif condition_type == ConditionType.IN_MAIN_OR_SIDEBOARD:
            return required_cards.issubset(all_cards)
        
        elif condition_type == ConditionType.ONE_OR_MORE_IN_MAINBOARD:
            return len(required_cards & mainboard_cards) >= 1
        
        elif condition_type == ConditionType.ONE_OR_MORE_IN_SIDEBOARD:
            return len(required_cards & sideboard_cards) >= 1
        
        elif condition_type == ConditionType.ONE_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            return len(required_cards & all_cards) >= 1
        
        elif condition_type == ConditionType.TWO_OR_MORE_IN_MAINBOARD:
            return len(required_cards & mainboard_cards) >= 2
        
        elif condition_type == ConditionType.TWO_OR_MORE_IN_SIDEBOARD:
            return len(required_cards & sideboard_cards) >= 2
        
        elif condition_type == ConditionType.TWO_OR_MORE_IN_MAIN_OR_SIDEBOARD:
            return len(required_cards & all_cards) >= 2
        
        elif condition_type == ConditionType.DOES_NOT_CONTAIN:
            return len(required_cards & all_cards) == 0
        
        elif condition_type == ConditionType.DOES_NOT_CONTAIN_MAINBOARD:
            return len(required_cards & mainboard_cards) == 0
        
        elif condition_type == ConditionType.DOES_NOT_CONTAIN_SIDEBOARD:
            return len(required_cards & sideboard_cards) == 0
        
        return False
    
    def _match_fallbacks(self, all_cards: Set[str], format_name: str) -> Optional[BadaroClassificationResult]:
        """Phase 2: Matcher contre les fallbacks (goodstuff decks)"""
        
        fallbacks = self.format_fallbacks[format_name]
        best_match = None
        best_score = 0
        
        for fallback_name, fallback_def in fallbacks.items():
            common_cards = set(fallback_def.common_cards)
            matches = len(common_cards & all_cards)
            
            # Calculer le pourcentage de match
            if len(common_cards) > 0:
                match_percentage = matches / len(common_cards)
                
                # Seuil minimum de 10% comme dans Badaro
                if match_percentage >= 0.1 and matches > best_score:
                    best_score = matches
                    best_match = fallback_def
        
        if best_match:
            color_identity = ""
            if best_match.include_color_in_name:
                color_identity = self._extract_color_identity(all_cards, format_name)
            
            return BadaroClassificationResult(
                archetype_name=best_match.name,
                confidence_score=60.0 + (best_score * 2),  # Score basé sur les matches
                matched_conditions=[f"Fallback: {best_score} common cards"],
                is_fallback=True,
                fallback_match_count=best_score,
                color_identity=color_identity
            )
        
        return None
    
    def _extract_color_identity(self, cards: Set[str], format_name: str) -> str:
        """Extraire l'identité colorielle selon la logique Badaro"""
        # Implémentation simplifiée - dans un vrai système utiliserait la DB complète
        colors = set()
        
        # Mapping basique pour les cartes courantes
        color_mapping = {
            # Mana fixing lands that indicate colors
            "Sacred Foundry": "RW", "Steam Vents": "UR", "Overgrown Tomb": "BG",
            "Temple Garden": "GW", "Watery Grave": "UB", "Stomping Ground": "RG",
            "Breeding Pool": "GU", "Godless Shrine": "WB", "Blood Crypt": "BR",
            "Hallowed Fountain": "WU",
            
            # Iconic spells
            "Lightning Bolt": "R", "Counterspell": "U", "Swords to Plowshares": "W",
            "Dark Ritual": "B", "Llanowar Elves": "G"
        }
        
        # Appliquer les overrides du format si disponibles
        overrides = self.color_overrides.get(format_name, {})
        
        for card in cards:
            if card in overrides.get("Lands", {}):
                card_colors = overrides["Lands"][card].get("Color", "")
                colors.update(list(card_colors))
            elif card in overrides.get("NonLands", {}):
                card_colors = overrides["NonLands"][card].get("Color", "")
                colors.update(list(card_colors))
            elif card in color_mapping:
                card_colors = color_mapping[card]
                colors.update(list(card_colors))
        
        # Convertir en string ordonnée WUBRG
        color_order = "WUBRG"
        return "".join([c for c in color_order if c in colors])
    
    def _color_classification(self, cards: Set[str]) -> BadaroClassificationResult:
        """Classification de dernière chance par couleur"""
        color_identity = self._extract_color_identity(cards, "")
        
        if not color_identity:
            archetype_name = "Unknown"
        elif len(color_identity) == 1:
            color_names = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}
            archetype_name = f"Mono {color_names.get(color_identity, 'Unknown')}"
        else:
            archetype_name = f"{color_identity} Deck"
        
        return BadaroClassificationResult(
            archetype_name=archetype_name,
            confidence_score=30.0,  # Faible confiance
            matched_conditions=["Color classification fallback"],
            color_identity=color_identity
        )
    
    def _unknown_classification(self) -> BadaroClassificationResult:
        """Classification par défaut"""
        return BadaroClassificationResult(
            archetype_name="Unknown",
            confidence_score=0.0,
            matched_conditions=[],
        )
    
    async def get_available_formats(self) -> List[str]:
        """Récupérer la liste des formats disponibles depuis Badaro"""
        try:
            api_url = f"https://api.github.com/repos/Badaro/MTGOFormatData/contents/Formats"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                dirs = [item["name"] for item in response.json() if item["type"] == "dir"]
                return sorted(dirs)
            
        except Exception as e:
            self.logger.error(f"Error fetching available formats: {e}")
        
        return ["Modern", "Standard", "Pioneer", "Legacy", "Vintage", "Pauper"]

# Instance globale
badaro_engine = BadaroArchetypeEngine() 