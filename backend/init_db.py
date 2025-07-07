#!/usr/bin/env python3
"""
Script d'initialisation de la base de données Metalyzr
Crée toutes les tables et insère des données de test
"""

from database import create_tables, get_db, SessionLocal
from models import Archetype, DetectionRule, Tournament, Card
from datetime import datetime
import json

def create_sample_data():
    """Crée des données d'exemple pour tester le système"""
    db = SessionLocal()
    
    try:
        # Archétypes de base
        archetypes = [
            {
                "name": "Mono-Red Aggro",
                "format": "Standard", 
                "category": "Aggro",
                "description": "Deck agressif mono-rouge",
                "color_identity": "R",
                "key_cards": ["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"]
            },
            {
                "name": "Azorius Control", 
                "format": "Standard",
                "category": "Control",
                "description": "Deck de contrôle blanc-bleu",
                "color_identity": "WU", 
                "key_cards": ["Counterspell", "Wrath of God", "Teferi"]
            },
            {
                "name": "Golgari Midrange",
                "format": "Standard",
                "category": "Midrange", 
                "description": "Deck midrange noir-vert",
                "color_identity": "BG",
                "key_cards": ["Tarmogoyf", "Liliana", "Abrupt Decay"]
            }
        ]
        
        # Insertion des archétypes
        for arch_data in archetypes:
            archetype = Archetype(**arch_data)
            db.add(archetype)
        
        # Cartes populaires
        cards = [
            {
                "name": "Lightning Bolt",
                "mana_cost": "{R}",
                "cmc": 1,
                "type_line": "Instant",
                "colors": "R",
                "color_identity": "R",
                "oracle_text": "Lightning Bolt deals 3 damage to any target.",
                "rarity": "common"
            },
            {
                "name": "Counterspell", 
                "mana_cost": "{U}{U}",
                "cmc": 2,
                "type_line": "Instant",
                "colors": "U",
                "color_identity": "U", 
                "oracle_text": "Counter target spell.",
                "rarity": "common"
            },
            {
                "name": "Tarmogoyf",
                "mana_cost": "{1}{G}",
                "cmc": 2,
                "type_line": "Creature — Lhurgoyf",
                "colors": "G",
                "color_identity": "G",
                "power": "*",
                "toughness": "*+1",
                "oracle_text": "Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
                "rarity": "rare"
            }
        ]
        
        # Insertion des cartes
        for card_data in cards:
            card = Card(**card_data)
            db.add(card)
            
        # Tournoi d'exemple
        tournament = Tournament(
            name="Standard Challenge #12345",
            format="Standard",
            date=datetime(2024, 1, 15),
            location="Magic Online",
            organizer="Wizards of the Coast",
            total_players=128,
            rounds=7,
            tournament_type="Swiss + Top 8",
            source_site="mtgo",
            is_complete=True
        )
        db.add(tournament)
        
        # Commit toutes les données
        db.commit()
        print("✅ Données d'exemple créées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation de la base de données Metalyzr...")
    
    # Créer toutes les tables
    print("📊 Création des tables...")
    create_tables()
    print("✅ Tables créées!")
    
    # Créer des données d'exemple
    print("📝 Insertion des données d'exemple...")
    create_sample_data()
    
    print("🎉 Base de données initialisée avec succès!")

if __name__ == "__main__":
    main() 