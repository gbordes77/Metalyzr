from typing import List, Dict, Optional
from sqlalchemy.orm import Session
# from ..models import Archetype, DetectionRule, Deck
import re

# Mock classes until models are fully integrated
class Archetype: pass
class DetectionRule: pass
class Deck: pass


class ArchetypeService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_archetype(self, data: Dict) -> Archetype:
        """Créer un nouvel archétype avec ses règles de détection"""
        archetype = Archetype(**data)
        # self.db.add(archetype)
        # self.db.commit()
        return archetype
    
    def add_detection_rule(self, archetype_id: int, rule_data: Dict) -> DetectionRule:
        """Ajouter une règle de détection à un archétype"""
        rule = DetectionRule(**rule_data)
        # archetype = self.db.query(Archetype).get(archetype_id)
        # if archetype:
        #     archetype.rules.append(rule)
        #     self.db.commit()
        return rule
    
    def detect_archetype(self, deck_list: List[str]) -> Optional[Archetype]:
        """Détecter automatiquement l'archétype d'un deck"""
        # rules = self.db.query(DetectionRule).filter_by(active=True).order_by(DetectionRule.priority.desc()).all()
        rules = [] # Mock
        
        best_match = None
        best_score = 0
        
        for rule in rules:
            score = self._evaluate_rule(deck_list, rule)
            if score > best_score:
                best_score = score
                best_match = rule.archetypes[0] if rule.archetypes else None
                
        return best_match if best_score >= 70 else None  # Seuil de confiance
    
    def _evaluate_rule(self, deck_list: List[str], rule: DetectionRule) -> int:
        """Évaluer une règle contre une liste de deck"""
        conditions = rule.conditions
        score = 0
        
        if rule.rule_type == 'contains_all':
            required_cards = conditions.get('cards', [])
            if all(card in deck_list for card in required_cards):
                score = rule.confidence_score
                
        elif rule.rule_type == 'contains_any':
            required_cards = conditions.get('cards', [])
            min_count = conditions.get('min_count', 1)
            count = sum(1 for card in required_cards if card in deck_list)
            if count >= min_count:
                score = rule.confidence_score * (count / len(required_cards))
                
        elif rule.rule_type == 'regex':
            pattern = conditions.get('pattern', '')
            matches = sum(1 for card in deck_list if re.search(pattern, card))
            if matches >= conditions.get('min_matches', 1):
                score = rule.confidence_score
                
        elif rule.rule_type == 'threshold':
            eval_func = conditions.get('function')
            if eval_func:
                score = eval_func(deck_list) * rule.confidence_score
                
        return score
    
    def merge_archetypes(self, source_id: int, target_id: int):
        """Fusionner deux archétypes (utile pour nettoyer les doublons)"""
        # source = self.db.query(Archetype).get(source_id)
        # target = self.db.query(Archetype).get(target_id)
        
        # if source and target:
        #     for deck in source.decks:
        #         deck.archetype_id = target_id
            
        #     for rule in source.rules:
        #         if rule not in target.rules:
        #             target.rules.append(rule)
            
        #     self.db.delete(source)
        #     self.db.commit()
        pass
    
    def suggest_archetype_updates(self) -> List[Dict]:
        """Suggérer des mises à jour d'archétypes basées sur les données récentes"""
        suggestions = []
        
        # unclassified = self.db.query(Deck).filter_by(archetype_id=None).all()
        # clusters = self._cluster_similar_decks(unclassified)
        
        # for cluster in clusters:
        #     if len(cluster) >= 5:
        #         suggestions.append({
        #             'type': 'new_archetype',
        #             'sample_decks': cluster[:3],
        #             'common_cards': self._find_common_cards(cluster),
        #             'suggested_name': self._generate_archetype_name(cluster)
        #         })
        
        return suggestions 