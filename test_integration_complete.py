"""
Tests d'intégration complets pour Metalyzr v2.0
Teste: API, Cache, Rate Limiting, Monitoring, Sécurité
"""
import pytest
import asyncio
import aiohttp
import time
from datetime import datetime

class TestMetalyzrIntegration:
    """Tests d'intégration complets"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    async def session(self):
        """Session HTTP pour les tests"""
        async with aiohttp.ClientSession() as session:
            yield session
    
    async def test_api_health_and_monitoring(self, session):
        """Test health check et métriques"""
        # Health check
        async with session.get(f"{self.BASE_URL}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data["status"] == "healthy"
            assert "cache_status" in data
            assert "version" in data
            assert data["version"] == "2.0.0"
            
        # Métriques Prometheus
        async with session.get(f"{self.BASE_URL}/metrics") as response:
            assert response.status == 200
            metrics_text = await response.text()
            assert "metalyzr_requests_total" in metrics_text
            assert "metalyzr_request_duration_seconds" in metrics_text
            assert "metalyzr_cache_hits_total" in metrics_text
    
    async def test_rate_limiting(self, session):
        """Test rate limiting fonctionne"""
        # Test normal - doit fonctionner
        async with session.get(f"{self.BASE_URL}/api/stats") as response:
            assert response.status == 200
            
        # Test burst - dépasser les limites (60/minute pour stats)
        start_time = time.time()
        success_count = 0
        rate_limited_count = 0
        
        # Faire 65 requêtes rapides
        for i in range(65):
            try:
                async with session.get(f"{self.BASE_URL}/api/stats") as response:
                    if response.status == 200:
                        success_count += 1
                    elif response.status == 429:  # Too Many Requests
                        rate_limited_count += 1
            except Exception:
                pass
                
        # Doit avoir des rate limits après 60 requêtes
        assert rate_limited_count > 0, "Rate limiting ne fonctionne pas"
        print(f"✅ Rate limiting: {success_count} succès, {rate_limited_count} limités")
    
    async def test_cors_security(self, session):
        """Test configuration CORS sécurisée"""
        headers = {
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        }
        
        async with session.options(f"{self.BASE_URL}/api/stats", headers=headers) as response:
            # Doit rejeter les origins non autorisées
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            assert cors_header != "*", "CORS trop permissif"
            
        # Test avec origin autorisé
        headers["Origin"] = "http://localhost:3000"
        async with session.options(f"{self.BASE_URL}/api/stats", headers=headers) as response:
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            assert cors_header == "http://localhost:3000", "CORS ne fonctionne pas correctement"
    
    async def test_cache_integration(self, session):
        """Test intégration cache MTGODecklistCache"""
        # Vérifier status cache
        async with session.get(f"{self.BASE_URL}/api/cache/status") as response:
            assert response.status == 200
            data = await response.json()
            assert "cache_status" in data
            
        # Test sync cache (rate limited à 3/minute)
        async with session.get(f"{self.BASE_URL}/api/cache/sync") as response:
            assert response.status == 200
            data = await response.json()
            assert "status" in data
            
        # Vérifier données chargées
        async with session.get(f"{self.BASE_URL}/api/tournaments") as response:
            assert response.status == 200
            tournaments = await response.json()
            assert isinstance(tournaments, list)
            
        async with session.get(f"{self.BASE_URL}/api/archetypes") as response:
            assert response.status == 200
            archetypes = await response.json()
            assert isinstance(archetypes, list)
    
    async def test_api_documentation(self, session):
        """Test documentation OpenAPI accessible"""
        # Documentation OpenAPI
        async with session.get(f"{self.BASE_URL}/docs") as response:
            assert response.status == 200
            
        # ReDoc
        async with session.get(f"{self.BASE_URL}/redoc") as response:
            assert response.status == 200
            
        # OpenAPI JSON schema
        async with session.get(f"{self.BASE_URL}/openapi.json") as response:
            assert response.status == 200
            schema = await response.json()
            assert "info" in schema
            assert "paths" in schema
            assert schema["info"]["title"] == "Metalyzr API"
            assert schema["info"]["version"] == "2.0.0"
    
    async def test_crud_operations(self, session):
        """Test opérations CRUD avec rate limiting"""
        # Créer un tournoi
        tournament_data = {
            "name": "Test Tournament Integration",
            "format": "Modern",
            "date": "2025-01-08",
            "participants": 32,
            "source": "test"
        }
        
        async with session.post(f"{self.BASE_URL}/api/tournaments", json=tournament_data) as response:
            assert response.status == 200
            tournament = await response.json()
            assert tournament["name"] == tournament_data["name"]
            tournament_id = tournament["id"]
            
        # Lire le tournoi créé
        async with session.get(f"{self.BASE_URL}/api/tournaments/{tournament_id}") as response:
            assert response.status == 200
            tournament = await response.json()
            assert tournament["name"] == tournament_data["name"]
            
        # Créer un archétype
        archetype_data = {
            "name": "Test Archetype Integration",
            "description": "Archétype de test d'intégration",
            "winRate": 75.5,
            "popularity": 12.3
        }
        
        async with session.post(f"{self.BASE_URL}/api/archetypes", json=archetype_data) as response:
            assert response.status == 200
            archetype = await response.json()
            assert archetype["name"] == archetype_data["name"]
    
    async def test_error_handling(self, session):
        """Test gestion d'erreurs et logging"""
        # Tournoi inexistant
        async with session.get(f"{self.BASE_URL}/api/tournaments/99999") as response:
            assert response.status == 404
            error = await response.json()
            assert "detail" in error
            
        # Données invalides
        invalid_data = {"invalid": "data"}
        async with session.post(f"{self.BASE_URL}/api/tournaments", json=invalid_data) as response:
            # Doit gérer gracieusement les données invalides
            data = await response.json()
            assert "id" in data  # Crée quand même avec des valeurs par défaut
    
    async def test_performance_baseline(self, session):
        """Test performance baseline"""
        # Mesurer latence API
        start_time = time.time()
        
        tasks = []
        for _ in range(10):
            task = session.get(f"{self.BASE_URL}/api/stats")
            tasks.append(task)
            
        responses = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        avg_latency = total_time / len(responses)
        
        # Toutes les requêtes doivent réussir
        for response in responses:
            assert response.status == 200
            response.close()
            
        # Latence moyenne doit être raisonnable
        assert avg_latency < 0.5, f"Latence trop élevée: {avg_latency:.3f}s"
        print(f"✅ Performance: {avg_latency:.3f}s latence moyenne")

# Tests pour le monitoring
class TestMonitoring:
    """Tests spécifiques au monitoring"""
    
    BASE_URL = "http://localhost:8000"
    
    async def test_prometheus_metrics_format(self, session):
        """Test format des métriques Prometheus"""
        async with session.get(f"{self.BASE_URL}/metrics") as response:
            assert response.status == 200
            metrics = await response.text()
            
            # Vérifier présence des métriques essentielles
            required_metrics = [
                "metalyzr_requests_total",
                "metalyzr_request_duration_seconds",
                "metalyzr_cache_hits_total",
                "metalyzr_api_errors_total"
            ]
            
            for metric in required_metrics:
                assert metric in metrics, f"Métrique manquante: {metric}"
                
            # Vérifier format Prometheus valide
            lines = metrics.split('\n')
            help_lines = [l for l in lines if l.startswith('# HELP')]
            type_lines = [l for l in lines if l.startswith('# TYPE')]
            
            assert len(help_lines) >= 4, "Pas assez de descriptions HELP"
            assert len(type_lines) >= 4, "Pas assez de types TYPE"
    
    @pytest.fixture
    async def session(self):
        """Session HTTP pour les tests"""
        async with aiohttp.ClientSession() as session:
            yield session

# Fonction principale pour exécuter les tests
async def run_integration_tests():
    """Exécuter tous les tests d'intégration"""
    print("🧪 Démarrage des tests d'intégration Metalyzr v2.0...")
    
    # Vérifier que l'API est accessible
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status != 200:
                    print("❌ API non accessible, démarrez le backend d'abord")
                    return False
    except Exception as e:
        print(f"❌ Erreur connexion API: {e}")
        return False
    
    # Exécuter les tests
    test_suite = TestMetalyzrIntegration()
    monitoring_suite = TestMonitoring()
    
    async with aiohttp.ClientSession() as session:
        try:
            # Tests API principaux
            await test_suite.test_api_health_and_monitoring(session)
            print("✅ Health check et monitoring")
            
            await test_suite.test_rate_limiting(session)
            print("✅ Rate limiting")
            
            await test_suite.test_cors_security(session)
            print("✅ Sécurité CORS")
            
            await test_suite.test_cache_integration(session)
            print("✅ Intégration cache")
            
            await test_suite.test_api_documentation(session)
            print("✅ Documentation API")
            
            await test_suite.test_crud_operations(session)
            print("✅ Opérations CRUD")
            
            await test_suite.test_error_handling(session)
            print("✅ Gestion d'erreurs")
            
            await test_suite.test_performance_baseline(session)
            print("✅ Performance baseline")
            
            # Tests monitoring
            await monitoring_suite.test_prometheus_metrics_format(session)
            print("✅ Métriques Prometheus")
            
            print("\n🎉 Tous les tests d'intégration passés avec succès!")
            return True
            
        except Exception as e:
            print(f"\n❌ Échec des tests: {e}")
            return False

if __name__ == "__main__":
    import asyncio
    
    # Installer les dépendances si nécessaire
    try:
        import aiohttp
        import pytest
    except ImportError:
        print("Installer les dépendances: pip install aiohttp pytest")
        exit(1)
    
    # Exécuter les tests
    success = asyncio.run(run_integration_tests())
    exit(0 if success else 1) 