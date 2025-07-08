#!/usr/bin/env python3
"""
Script de test pour l'intégration MTGODecklistCache dans Metalyzr
Valide que le cache fonctionne correctement et fournit des données réelles
"""
import asyncio
import sys
import time
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.append(str(Path(__file__).parent / "backend"))

from cache_manager import mtgo_cache_manager

async def test_cache_integration():
    """Test complet de l'intégration cache"""
    print("🧪 Test d'intégration MTGODecklistCache")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # 1. Test d'initialisation
        print("\n1️⃣ Test d'initialisation du cache...")
        async with mtgo_cache_manager as cache:
            success = await cache.initialize()
            
            if success:
                print("✅ Cache initialisé avec succès")
            else:
                print("❌ Échec d'initialisation du cache")
                return False
            
            # 2. Test des statistiques
            print("\n2️⃣ Test des statistiques du cache...")
            stats = await cache.get_cache_stats()
            print(f"📊 Statistiques:")
            print(f"   - Tournois: {stats.get('total_tournaments', 0)}")
            print(f"   - Taille cache: {stats.get('cache_size_mb', 0)} MB")
            print(f"   - Dernière MAJ: {stats.get('last_update', 'N/A')}")
            print(f"   - Formats: {stats.get('formats', {})}")
            print(f"   - Plage dates: {stats.get('date_range', {})}")
            
            # 3. Test récupération tournois Modern
            print("\n3️⃣ Test récupération tournois Modern...")
            modern_tournaments = await cache.get_tournaments(
                format_filter="Modern",
                limit=5
            )
            print(f"📋 {len(modern_tournaments)} tournois Modern trouvés")
            
            for i, tournament in enumerate(modern_tournaments[:3]):
                print(f"   {i+1}. {tournament.get('name', 'Sans nom')} "
                      f"({tournament.get('date', 'N/A')}) - "
                      f"{len(tournament.get('decks', []))} decks")
            
            # 4. Test récupération tournois Standard
            print("\n4️⃣ Test récupération tournois Standard...")
            standard_tournaments = await cache.get_tournaments(
                format_filter="Standard", 
                limit=3
            )
            print(f"📋 {len(standard_tournaments)} tournois Standard trouvés")
            
            # 5. Test des archétypes
            print("\n5️⃣ Test détection archétypes...")
            all_archetypes = set()
            
            for tournament in modern_tournaments[:3]:
                for deck in tournament.get("decks", []):
                    archetype = deck.get("archetype")
                    if archetype and archetype != "Unknown":
                        all_archetypes.add(archetype)
            
            print(f"🎯 {len(all_archetypes)} archétypes uniques détectés:")
            for archetype in sorted(all_archetypes)[:10]:
                print(f"   - {archetype}")
            
            # 6. Test de synchronisation
            print("\n6️⃣ Test de synchronisation...")
            if len(modern_tournaments) < 5:
                print("⚠️ Peu de données, test de sync...")
                sync_success = await cache.sync_from_remote()
                if sync_success:
                    print("✅ Synchronisation réussie")
                else:
                    print("❌ Échec de synchronisation")
            else:
                print("✅ Cache déjà bien alimenté, pas de sync nécessaire")
    
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    elapsed = time.time() - start_time
    print(f"\n🎉 Tests terminés en {elapsed:.2f}s")
    return True

async def test_api_integration():
    """Test l'intégration avec l'API"""
    print("\n🔗 Test intégration API...")
    
    try:
        # Simuler le chargement de données dans l'API
        import sys
        sys.path.append("backend")
        from main_simple import load_cache_data, REAL_DATA
        
        # Charger les données
        await load_cache_data()
        
        print(f"✅ API integration:")
        print(f"   - Tournois chargés: {len(REAL_DATA['tournaments'])}")
        print(f"   - Archétypes: {len(REAL_DATA['archetypes'])}")
        print(f"   - Decks total: {REAL_DATA['stats']['decks']}")
        print(f"   - Cache status: {REAL_DATA['stats']['cache_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Lancement des tests d'intégration Metalyzr + MTGODecklistCache")
    
    async def run_all_tests():
        # Test 1: Cache
        cache_ok = await test_cache_integration()
        
        # Test 2: API
        api_ok = await test_api_integration()
        
        print("\n" + "=" * 50)
        print("📋 RÉSULTATS FINAUX:")
        print(f"   Cache Integration: {'✅ OK' if cache_ok else '❌ ÉCHEC'}")
        print(f"   API Integration: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
        
        if cache_ok and api_ok:
            print("\n🎉 TOUS LES TESTS PASSENT!")
            print("🚀 Metalyzr est prêt avec des données réelles!")
            return 0
        else:
            print("\n❌ CERTAINS TESTS ÉCHOUENT")
            print("🔧 Vérifiez la configuration et la connectivité")
            return 1
    
    return asyncio.run(run_all_tests())

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 