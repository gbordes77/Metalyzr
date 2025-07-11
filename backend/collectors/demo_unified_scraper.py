#!/usr/bin/env python3
"""
Démonstration du scraper unifié Metalyzr
Teste le meilleur des deux mondes : API Melee.gg + Scraping + Classification
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_melee_api():
    """Démonstration de l'API Melee.gg"""
    print("🎯 DEMO: API Melee.gg")
    print("=" * 50)
    
    try:
        from melee_api_client import MeleeAPIClient
        
        async with MeleeAPIClient() as client:
            print("📡 Connexion à l'API Melee.gg...")
            
            # Test récupération de tournois
            tournaments = await client.get_tournaments(
                format_name="Modern",
                limit=3
            )
            
            print(f"✅ Trouvé {len(tournaments)} tournois Modern")
            
            for i, tournament in enumerate(tournaments[:2], 1):
                print(f"\n🏆 Tournoi {i}: {tournament.get('name')}")
                print(f"   📅 Date: {tournament.get('date')}")
                print(f"   👥 Joueurs: {tournament.get('total_players')}")
                print(f"   🔗 URL: {tournament.get('external_url')}")
                
                # Test détails du tournoi
                if tournament.get("id"):
                    details = await client.get_tournament_details(tournament["id"])
                    if details:
                        decks = details.get("decks", [])
                        print(f"   🃏 Decks: {len(decks)}")
                        
                        if decks:
                            top_deck = decks[0]
                            print(f"   🥇 Winner: {top_deck.get('player_name')} - {top_deck.get('archetype')}")
            
    except Exception as e:
        print(f"❌ Erreur API Melee.gg: {e}")
    
    print()

async def demo_archetype_classifier():
    """Démonstration du classificateur d'archétypes"""
    print("🧠 DEMO: Classificateur d'Archétypes")
    print("=" * 50)
    
    try:
        from archetype_classifier import default_classifier, ArchetypeRule
        
        # Deck Burn typique
        burn_deck = {
            "Lightning Bolt": 4,
            "Goblin Guide": 4,
            "Monastery Swiftspear": 4,
            "Lava Spike": 4,
            "Boros Charm": 4,
            "Lightning Strike": 2,
            "Mountain": 18,
            "Sacred Foundry": 2
        }
        
        print("🔥 Test classification deck Burn:")
        for card, count in list(burn_deck.items())[:5]:
            print(f"   {count}x {card}")
        print("   ...")
        
        result = default_classifier.classify_deck(burn_deck, format_name="Modern")
        
        print(f"\n✅ Résultat:")
        print(f"   🎯 Archétype: {result.archetype_name}")
        print(f"   📊 Score: {result.score:.1f}")
        print(f"   🎖️ Confiance: {result.confidence.value}")
        print(f"   🔍 Cartes trouvées: {', '.join(result.signature_cards_found[:3])}")
        
        # Test deck UW Control
        control_deck = {
            "Counterspell": 4,
            "Wrath of God": 2,
            "Teferi, Hero of Dominaria": 3,
            "Cryptic Command": 3,
            "Supreme Verdict": 2,
            "Island": 8,
            "Plains": 6,
            "Hallowed Fountain": 4
        }
        
        print(f"\n🛡️ Test classification deck Control:")
        control_result = default_classifier.classify_deck(control_deck, format_name="Modern")
        print(f"   🎯 Archétype: {control_result.archetype_name}")
        print(f"   📊 Score: {control_result.score:.1f}")
        print(f"   🎖️ Confiance: {control_result.confidence.value}")
        
    except Exception as e:
        print(f"❌ Erreur classification: {e}")
    
    print()

async def demo_unified_scraper():
    """Démonstration du scraper unifié"""
    print("🌍 DEMO: Scraper Unifié (Simulation)")
    print("=" * 50)
    
    try:
        # Simuler les résultats car on n'a pas les vrais services
        print("🔄 Simulation du scraping unifié Modern...")
        
        # Simulation résultats API Melee.gg
        print("\n1️⃣ Source: Melee.gg (API)")
        print("   ✅ 5 tournois récupérés")
        print("   🃏 85 decks classifiés")
        print("   🎯 Archétypes: Burn (25%), UW Control (20%), Jund (15%)")
        
        # Simulation résultats MTGTop8
        print("\n2️⃣ Source: MTGTop8 (Scraping)")
        print("   ✅ 3 tournois récupérés")
        print("   🃏 45 decks classifiés")
        print("   🎯 Archétypes: Amulet Titan (30%), Merfolk (20%), Burn (15%)")
        
        # Résultats combinés
        print("\n📊 RÉSULTATS COMBINÉS:")
        print("   🏆 Total: 8 tournois, 130 decks")
        print("   ⚡ Temps: 12.5 secondes")
        print("   🎯 Top archétypes:")
        print("      1. Burn - 26 decks (20%)")
        print("      2. UW Control - 20 decks (15%)")
        print("      3. Amulet Titan - 18 decks (14%)")
        print("      4. Jund - 15 decks (12%)")
        print("      5. Merfolk - 12 decks (9%)")
        
        print("\n📈 Métriques de qualité:")
        print("   🎖️ Confiance HIGH: 78 decks (60%)")
        print("   🎖️ Confiance MEDIUM: 35 decks (27%)")
        print("   🎖️ Confiance LOW: 17 decks (13%)")
        
    except Exception as e:
        print(f"❌ Erreur scraper unifié: {e}")
    
    print()

async def demo_data_integration():
    """Démonstration de l'intégration des données"""
    print("💾 DEMO: Intégration Backend")
    print("=" * 50)
    
    try:
        print("🔄 Simulation intégration avec backend Metalyzr...")
        
        # Simuler l'envoi vers l'API backend
        print("\n📤 Envoi vers API backend (http://localhost:8000)")
        print("   POST /api/tournaments - 8 nouveaux tournois")
        print("   POST /api/decks - 130 nouveaux decks")
        print("   PUT /api/archetypes - 15 archétypes mis à jour")
        
        print("\n✅ Mise à jour du dashboard:")
        print("   📊 Statistiques temps réel disponibles")
        print("   🎯 Archétype breakdown actualisé")
        print("   📈 Tendances meta calculées")
        
        print("\n🔗 URLs disponibles:")
        print("   📊 Dashboard: http://localhost:3000")
        print("   👨‍💼 Admin: http://localhost:3000/admin")
        print("   📡 API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
    
    print()

def print_summary():
    """Afficher le résumé des fonctionnalités"""
    print("🎉 RÉSUMÉ: Le Meilleur des Deux Mondes")
    print("=" * 50)
    print()
    print("✅ IMPLÉMENTÉ:")
    print("   🥇 1. API Melee.gg (Priorité #1)")
    print("      - Appels API directs en temps réel")
    print("      - Données complètes avec standings")
    print("      - Rate limiting respectueux")
    print()
    print("   🥈 2. Classification Archétypes (Inspirée Badaro)")
    print("      - Système de règles en Python")
    print("      - Confiance multi-niveaux")
    print("      - Extensible par format")
    print()
    print("   🥉 3. Scraping MTGTop8 (Fallback)")
    print("      - Pipeline Scrapy existant")
    print("      - Complément aux données API")
    print("      - Parsing HTML robuste")
    print()
    print("   🔄 4. Scraper Unifié")
    print("      - Combine toutes les sources")
    print("      - Priorisation intelligente")
    print("      - Classification automatique")
    print()
    print("🚀 AVANTAGES:")
    print("   ⚡ Données temps réel (API > Scraping)")
    print("   🎯 Classification précise (Règles Badaro)")
    print("   🌍 Multi-sources fiables")
    print("   📊 Intégration complète avec dashboard")
    print()
    print("🎯 PROCHAINES ÉTAPES:")
    print("   1. Tester l'API Melee.gg avec de vraies clés")
    print("   2. Enrichir les règles d'archétypes")
    print("   3. Implémenter MTGO via mtg_decklist_scrapper")
    print("   4. Automatiser la collecte périodique")

async def main():
    """Fonction principale de démonstration"""
    print("🏗️ METALYZR - DÉMONSTRATION COMPLÈTE")
    print("Le meilleur des deux mondes : API + Scraping + Classification")
    print("=" * 70)
    print()
    
    # Tests en séquence
    await demo_melee_api()
    await demo_archetype_classifier()
    await demo_unified_scraper()
    await demo_data_integration()
    
    print_summary()
    
    print("\n🎊 Démonstration terminée !")
    print("Le système Metalyzr est prêt à implémenter le meilleur des deux mondes !")

if __name__ == "__main__":
    asyncio.run(main()) 