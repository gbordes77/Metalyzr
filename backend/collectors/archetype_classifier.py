"""
Classificateur d'archétypes basé sur des règles
Inspiré de MTGOArchetypeParser (Badaro) mais adapté en Python pour Metalyzr
"""
import logging
import re
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

class ArchetypeConfidence(Enum):
    """Niveaux de confiance pour la classification"""
    HIGH = "high"        # 90%+ confiance
    MEDIUM = "medium"    # 70-89% confiance  
    LOW = "low"         # 50-69% confiance
    UNKNOWN = "unknown"  # <50% confiance

@dataclass
class ArchetypeRule:
    """Règle de détection d'archétype"""
    name: str
    required_cards: List[str] = None      # Cartes obligatoires
    signature_cards: List[str] = None     # Cartes signature (bonus)
    forbidden_cards: List[str] = None     # Cartes interdites
    min_card_count: Dict[str, int] = None # Nombre minimum de cartes
    color_identity: Set[str] = None       # Couleurs requises
    weight: float = 1.0                   # Poids de la règle
    format_specific: List[str] = None     # Formats où applicable
    
    def __post_init__(self):
        if self.required_cards is None:
            self.required_cards = []
        if self.signature_cards is None:
            self.signature_cards = []
        if self.forbidden_cards is None:
            self.forbidden_cards = []
        if self.min_card_count is None:
            self.min_card_count = {}
        if self.color_identity is None:
            self.color_identity = set()
        if self.format_specific is None:
            self.format_specific = []

@dataclass
class ArchetypeMatch:
    """Résultat de classification d'un archétype"""
    archetype_name: str
    confidence: ArchetypeConfidence
    score: float
    matched_rules: List[str]
    signature_cards_found: List[str]
    missing_cards: List[str]

class ArchetypeClassifier:
    """
    Classificateur d'archétypes MTG basé sur des règles
    Inspiré de la logique MTGOArchetypeParser
    """
    
    def __init__(self):
        self.logger = logging.getLogger("scraper.archetype_classifier")
        self.rules: Dict[str, List[ArchetypeRule]] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Charger les règles par défaut pour les archétypes populaires"""
        
        # Modern Archetypes
        modern_rules = [
            # Aggro/Burn
            ArchetypeRule(
                name="Burn",
                required_cards=["Lightning Bolt"],
                signature_cards=["Goblin Guide", "Monastery Swiftspear", "Lava Spike", "Boros Charm"],
                min_card_count={"Lightning Bolt": 4, "burn_spells": 12},
                color_identity={"R"},
                weight=1.0
            ),
            
            # Control
            ArchetypeRule(
                name="UW Control", 
                required_cards=["Counterspell", "Wrath of God"],
                signature_cards=["Teferi, Hero of Dominaria", "Cryptic Command", "Supreme Verdict"],
                forbidden_cards=["Lightning Bolt", "Tarmogoyf"],
                color_identity={"U", "W"},
                weight=1.0
            ),
            
            # Combo
            ArchetypeRule(
                name="Amulet Titan",
                required_cards=["Amulet of Vigor", "Primeval Titan"],
                signature_cards=["Simic Growth Chamber", "Tolaria West", "Summoner's Pact"],
                min_card_count={"Amulet of Vigor": 4, "Primeval Titan": 4},
                weight=1.0
            ),
            
            # Midrange
            ArchetypeRule(
                name="Jund", 
                required_cards=["Tarmogoyf", "Lightning Bolt"],
                signature_cards=["Liliana of the Veil", "Bloodbraid Elf", "Inquisition of Kozilek"],
                color_identity={"B", "R", "G"},
                weight=1.0
            ),
            
            # Tribal
            ArchetypeRule(
                name="Merfolk",
                required_cards=["Lord of Atlantis"],
                signature_cards=["Force of Negation", "Merrow Reejerey", "Silvergill Adept"],
                min_card_count={"merfolk_creatures": 20},
                color_identity={"U"},
                weight=1.0
            ),
        ]
        
        # Standard Archetypes  
        standard_rules = [
            ArchetypeRule(
                name="Mono Red Aggro",
                required_cards=["Lightning Strike"],
                signature_cards=["Goblin Chainwhirler", "Hazoret the Fervent"],
                color_identity={"R"},
                weight=1.0
            ),
            
            ArchetypeRule(
                name="Esper Control",
                required_cards=["Teferi, Hero of Dominaria"],
                signature_cards=["Vraska's Contempt", "Seal Away", "Search for Azcanta"],
                color_identity={"W", "U", "B"},
                weight=1.0
            )
        ]
        
        self.rules["Modern"] = modern_rules
        self.rules["Standard"] = standard_rules
        self.rules["Legacy"] = []  # À définir
        self.rules["Pioneer"] = []  # À définir
    
    def classify_deck(self, mainboard: Dict[str, int], 
                     sideboard: Dict[str, int] = None,
                     format_name: str = "Modern") -> ArchetypeMatch:
        """
        Classifier un deck selon les règles d'archétypes
        
        Args:
            mainboard: Cartes du mainboard {nom: quantité}
            sideboard: Cartes du sideboard {nom: quantité}
            format_name: Format du deck
            
        Returns:
            ArchetypeMatch avec le meilleur match trouvé
        """
        if sideboard is None:
            sideboard = {}
            
        format_rules = self.rules.get(format_name, [])
        if not format_rules:
            return self._unknown_archetype()
        
        all_cards = {**mainboard, **sideboard}
        card_names = set(all_cards.keys())
        
        matches = []
        
        for rule in format_rules:
            match_result = self._evaluate_rule(rule, all_cards, card_names, mainboard)
            if match_result.score > 0:
                matches.append(match_result)
        
        # Trier par score décroissant
        matches.sort(key=lambda x: x.score, reverse=True)
        
        if matches:
            best_match = matches[0]
            # Ajuster la confiance selon le score
            best_match.confidence = self._calculate_confidence(best_match.score)
            return best_match
        
        return self._unknown_archetype()
    
    def _evaluate_rule(self, rule: ArchetypeRule, 
                      all_cards: Dict[str, int],
                      card_names: Set[str],
                      mainboard: Dict[str, int]) -> ArchetypeMatch:
        """Évaluer une règle d'archétype contre un deck"""
        
        score = 0.0
        matched_rules = []
        signature_cards_found = []
        missing_cards = []
        
        # Vérifier les cartes requises
        required_score = 0
        for card in rule.required_cards:
            if card in card_names:
                required_score += 1
                matched_rules.append(f"Required: {card}")
            else:
                missing_cards.append(card)
        
        # Si toutes les cartes requises ne sont pas là, score faible
        if len(rule.required_cards) > 0:
            required_ratio = required_score / len(rule.required_cards)
            if required_ratio < 0.5:  # Moins de 50% des cartes requises
                return ArchetypeMatch(
                    archetype_name=rule.name,
                    confidence=ArchetypeConfidence.UNKNOWN,
                    score=0.0,
                    matched_rules=[],
                    signature_cards_found=[],
                    missing_cards=missing_cards
                )
            score += required_ratio * 40  # 40 points max pour les cartes requises
        
        # Vérifier les cartes signature (bonus)
        signature_score = 0
        for card in rule.signature_cards:
            if card in card_names:
                signature_score += 1
                signature_cards_found.append(card)
                matched_rules.append(f"Signature: {card}")
        
        if len(rule.signature_cards) > 0:
            signature_ratio = signature_score / len(rule.signature_cards)
            score += signature_ratio * 30  # 30 points max pour les cartes signature
        
        # Vérifier les cartes interdites (malus)
        forbidden_found = 0
        for card in rule.forbidden_cards:
            if card in card_names:
                forbidden_found += 1
                score -= 20  # -20 points par carte interdite
        
        # Vérifier les comptages minimums
        for card, min_count in rule.min_card_count.items():
            actual_count = all_cards.get(card, 0)
            if actual_count >= min_count:
                score += 10
                matched_rules.append(f"Count: {card} >= {min_count}")
            else:
                score -= 5
        
        # Vérifier l'identité colorielle (si spécifiée)
        if rule.color_identity:
            deck_colors = self._extract_colors(card_names)
            color_match = len(rule.color_identity.intersection(deck_colors)) / len(rule.color_identity)
            score += color_match * 20  # 20 points max pour les couleurs
        
        # Appliquer le poids de la règle
        score *= rule.weight
        
        return ArchetypeMatch(
            archetype_name=rule.name,
            confidence=ArchetypeConfidence.UNKNOWN,  # Sera calculé plus tard
            score=max(0, score),  # Score minimum de 0
            matched_rules=matched_rules,
            signature_cards_found=signature_cards_found,
            missing_cards=missing_cards
        )
    
    def _calculate_confidence(self, score: float) -> ArchetypeConfidence:
        """Calculer le niveau de confiance selon le score"""
        if score >= 90:
            return ArchetypeConfidence.HIGH
        elif score >= 70:
            return ArchetypeConfidence.MEDIUM
        elif score >= 50:
            return ArchetypeConfidence.LOW
        else:
            return ArchetypeConfidence.UNKNOWN
    
    def _extract_colors(self, card_names: Set[str]) -> Set[str]:
        """
        Extraire les couleurs d'un deck basé sur les noms de cartes
        Version simplifiée - dans un vrai système, on utiliserait une DB de cartes
        """
        colors = set()
        
        # Mapping basique des cartes connues vers leurs couleurs
        color_mapping = {
            # Cartes rouges
            "Lightning Bolt": "R", "Goblin Guide": "R", "Lava Spike": "R",
            "Monastery Swiftspear": "R", "Lightning Strike": "R",
            
            # Cartes bleues  
            "Counterspell": "U", "Cryptic Command": "U", "Force of Negation": "U",
            "Lord of Atlantis": "U", "Teferi, Hero of Dominaria": "UW",
            
            # Cartes blanches
            "Wrath of God": "W", "Supreme Verdict": "UW", "Swords to Plowshares": "W",
            
            # Cartes noires
            "Liliana of the Veil": "B", "Inquisition of Kozilek": "B",
            "Vraska's Contempt": "B",
            
            # Cartes vertes
            "Tarmogoyf": "G", "Primeval Titan": "G",
            
            # Multicolores
            "Boros Charm": "RW", "Bloodbraid Elf": "RG"
        }
        
        for card in card_names:
            if card in color_mapping:
                card_colors = color_mapping[card]
                colors.update(list(card_colors))
        
        return colors
    
    def _unknown_archetype(self) -> ArchetypeMatch:
        """Retourner un match 'Unknown' par défaut"""
        return ArchetypeMatch(
            archetype_name="Unknown",
            confidence=ArchetypeConfidence.UNKNOWN,
            score=0.0,
            matched_rules=[],
            signature_cards_found=[],
            missing_cards=[]
        )
    
    def add_custom_rule(self, format_name: str, rule: ArchetypeRule):
        """Ajouter une règle personnalisée"""
        if format_name not in self.rules:
            self.rules[format_name] = []
        self.rules[format_name].append(rule)
        self.logger.info(f"Added custom rule '{rule.name}' for format {format_name}")
    
    def get_format_archetypes(self, format_name: str) -> List[str]:
        """Obtenir la liste des archétypes disponibles pour un format"""
        format_rules = self.rules.get(format_name, [])
        return [rule.name for rule in format_rules]

# Instance globale pour l'utilisation
default_classifier = ArchetypeClassifier() 