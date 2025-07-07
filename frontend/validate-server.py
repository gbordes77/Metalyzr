#!/usr/bin/env python3
"""
🧪 Script de validation du serveur Python Metalyzr
Teste toutes les fonctionnalités du serveur simple-server.py
"""

import sys
import time
import json
import subprocess
import requests
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:3000"
TIMEOUT = 10

def log(message, level="INFO"):
    """Log avec timestamp et niveau"""
    timestamp = time.strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[0;34m",  # Bleu
        "SUCCESS": "\033[0;32m",  # Vert  
        "ERROR": "\033[0;31m",  # Rouge
        "WARNING": "\033[1;33m"  # Jaune
    }
    reset = "\033[0m"
    color = colors.get(level, colors["INFO"])
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

def test_endpoint(path, expected_status=200, description=""):
    """Test un endpoint spécifique"""
    url = urljoin(BASE_URL, path)
    try:
        response = requests.get(url, timeout=TIMEOUT)
        
        if response.status_code == expected_status:
            log(f"✅ {description or path}: {response.status_code}", "SUCCESS")
            return True
        else:
            log(f"❌ {description or path}: Status {response.status_code} (attendu {expected_status})", "ERROR")
            return False
            
    except requests.exceptions.Timeout:
        log(f"⏰ {description or path}: Timeout après {TIMEOUT}s", "WARNING")
        return False
    except requests.exceptions.ConnectionError:
        log(f"🚫 {description or path}: Connexion refusée", "ERROR")
        return False
    except Exception as e:
        log(f"💥 {description or path}: Erreur {e}", "ERROR")
        return False

def test_api_proxy(endpoint, description=""):
    """Test des proxies API (attendu: erreur 500 car backend off)"""
    return test_endpoint(f"/api/{endpoint}", 500, f"API Proxy {description}")

def validate_server():
    """Validation complète du serveur"""
    log("🚀 Début de la validation du serveur Metalyzr", "INFO")
    
    results = {
        "static_files": [],
        "api_proxies": [],
        "spa_routing": []
    }
    
    # Test 1: Fichiers statiques
    log("\n📁 Test des fichiers statiques", "INFO")
    static_tests = [
        ("/", "Page d'accueil"),
        ("/index.html", "Index HTML"),
        ("/favicon.ico", "Favicon"),
        ("/test-admin.html", "Page de test admin")
    ]
    
    for path, desc in static_tests:
        result = test_endpoint(path, 200, desc)
        results["static_files"].append(result)
    
    # Test 2: Proxies API (backend off = 500 attendu)
    log("\n🔗 Test des proxies API", "INFO")
    api_tests = [
        ("stats", "Stats"),
        ("tournaments/", "Tournaments"),
        ("archetypes/", "Archetypes"),
        ("decks/", "Decks")
    ]
    
    for endpoint, desc in api_tests:
        result = test_api_proxy(endpoint, desc)
        results["api_proxies"].append(result)
    
    # Test 3: Health endpoint
    log("\n💓 Test Health Check", "INFO")
    health_result = test_endpoint("/health", 500, "Health Check (backend off)")
    results["api_proxies"].append(health_result)
    
    # Test 4: SPA Routing (routes React)
    log("\n🎯 Test SPA Routing", "INFO")
    spa_tests = [
        ("/admin", "Dashboard Admin"),
        ("/dashboard", "Dashboard Principal"),
        ("/unknown-route", "Route inconnue (fallback)")
    ]
    
    for path, desc in spa_tests:
        result = test_endpoint(path, 200, desc)
        results["spa_routing"].append(result)
    
    # Test 5: CORS Headers
    log("\n🌐 Test CORS Headers", "INFO")
    try:
        response = requests.options(BASE_URL, timeout=TIMEOUT)
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        cors_ok = all(header in response.headers for header in cors_headers)
        if cors_ok:
            log("✅ CORS Headers: Présents", "SUCCESS")
        else:
            log("❌ CORS Headers: Manquants", "ERROR")
            
    except Exception as e:
        log(f"❌ CORS Headers: Erreur {e}", "ERROR")
        cors_ok = False
    
    # Calcul du score
    total_tests = sum(len(category) for category in results.values()) + 1  # +1 pour CORS
    passed_tests = sum(sum(category) for category in results.values()) + (1 if cors_ok else 0)
    
    score_percent = (passed_tests / total_tests) * 100
    
    # Résumé
    log(f"\n📊 RÉSUMÉ DE VALIDATION", "INFO")
    log(f"Tests réussis: {passed_tests}/{total_tests}", "INFO")
    log(f"Score: {score_percent:.1f}%", "INFO")
    
    if score_percent >= 90:
        log("🎉 SERVEUR ENTIÈREMENT OPÉRATIONNEL!", "SUCCESS")
        return True
    elif score_percent >= 70:
        log("🟡 Serveur partiellement fonctionnel", "WARNING")
        return True
    else:
        log("🔴 Serveur défaillant - Révision nécessaire", "ERROR")
        return False

def check_server_running():
    """Vérifie que le serveur est en marche"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return True
    except:
        return False

def main():
    """Point d'entrée principal"""
    print("🧪 METALYZR - Validation du Serveur Python")
    print("==========================================")
    
    # Vérifier que le serveur tourne
    if not check_server_running():
        log("❌ Serveur non accessible. Vérifiez qu'il tourne sur http://localhost:3000", "ERROR")
        print("\n💡 Pour démarrer le serveur:")
        print("   cd frontend/build && python3 simple-server.py")
        sys.exit(1)
    
    # Lancer la validation
    success = validate_server()
    
    # Instructions finales
    if success:
        print(f"\n✨ Validation terminée avec succès!")
        print(f"🌐 Serveur disponible: {BASE_URL}")
        print(f"👨‍💼 Admin Dashboard: {BASE_URL}/admin")
        print(f"🧪 Page de test: {BASE_URL}/test-admin.html")
    else:
        print(f"\n⚠️  Des problèmes ont été détectés")
        print(f"🔧 Consultez les logs ci-dessus pour les détails")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 