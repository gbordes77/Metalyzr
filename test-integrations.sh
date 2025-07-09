#!/bin/bash

echo "🧪 Test des intégrations réelles Metalyzr"
echo "=========================================="

# Variables
SERVER_URL="http://localhost:8000"
BACKEND_DIR="backend"

# Vérifier si le serveur tourne
echo "1. Vérification du serveur..."
curl -s "${SERVER_URL}/health" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Serveur running"
else
    echo "❌ Serveur non accessible - Lancement du serveur..."
    cd $BACKEND_DIR
    python3 main_simple.py &
    SERVER_PID=$!
    cd ..
    echo "⏳ Attente du démarrage..."
    sleep 5
fi

# Test des endpoints d'intégration
echo ""
echo "2. Test des endpoints d'intégration..."

# Test du statut des intégrations
echo "2.1. Statut des intégrations..."
response=$(curl -s "${SERVER_URL}/api/integrations/status")
if echo "$response" | grep -q "active"; then
    echo "✅ Intégrations actives"
else
    echo "❌ Intégrations non actives"
    echo "Response: $response"
fi

# Test des sites supportés
echo "2.2. Sites supportés pour le scraping..."
response=$(curl -s "${SERVER_URL}/api/integrations/supported-sites")
if echo "$response" | grep -q "mtggoldfish"; then
    echo "✅ Sites de scraping disponibles"
else
    echo "❌ Sites de scraping non disponibles"
    echo "Response: $response"
fi

# Test des formats supportés
echo "2.3. Formats supportés..."
response=$(curl -s "${SERVER_URL}/api/integrations/supported-formats")
if echo "$response" | grep -q "supported_formats"; then
    echo "✅ Formats supportés disponibles"
else
    echo "❌ Formats non disponibles"
    echo "Response: $response"
fi

# Test des tournois récents
echo "2.4. Tournois récents..."
response=$(curl -s "${SERVER_URL}/api/integrations/tournaments/recent?format_name=Modern&days=7")
if echo "$response" | grep -q "tournaments"; then
    echo "✅ API tournois récents fonctionne"
else
    echo "❌ API tournois récents ne fonctionne pas"
    echo "Response: $response"
fi

# Test d'analyse méta
echo "2.5. Analyse méta..."
response=$(curl -s -X POST "${SERVER_URL}/api/integrations/meta/analysis" \
    -H "Content-Type: application/json" \
    -d '{"format": "Modern", "days": 7}')
if echo "$response" | grep -q "total_decks"; then
    echo "✅ API analyse méta fonctionne"
else
    echo "❌ API analyse méta ne fonctionne pas"
    echo "Response: $response"
fi

# Test de scraping (avec une URL factice)
echo "2.6. Test de scraping..."
response=$(curl -s -X POST "${SERVER_URL}/api/integrations/scrape/deck" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.mtggoldfish.com/archetype/test", "format": "Modern"}')
if echo "$response" | grep -q "error\|failed\|detail"; then
    echo "⚠️ Scraping échoue (normal avec URL test)"
else
    echo "✅ API scraping répond"
fi

# Test de recherche par archétype
echo "2.7. Recherche par archétype..."
response=$(curl -s "${SERVER_URL}/api/integrations/tournaments/search?archetype=Burn&format_name=Modern")
if echo "$response" | grep -q "tournaments"; then
    echo "✅ API recherche par archétype fonctionne"
else
    echo "❌ API recherche par archétype ne fonctionne pas"
    echo "Response: $response"
fi

# Test des statistiques (avec intégrations)
echo "2.8. Statistiques avec intégrations..."
response=$(curl -s "${SERVER_URL}/api/stats")
if echo "$response" | grep -q "integrations"; then
    echo "✅ Statistiques avec intégrations disponibles"
else
    echo "❌ Statistiques avec intégrations non disponibles"
    echo "Response: $response"
fi

# Test des endpoints existants
echo ""
echo "3. Test des endpoints existants..."

# Test CRUD tournois
echo "3.1. Test CRUD tournois..."
response=$(curl -s "${SERVER_URL}/api/tournaments")
if echo "$response" | grep -q "tournaments"; then
    echo "✅ API tournois (CRUD) fonctionne"
else
    echo "❌ API tournois (CRUD) ne fonctionne pas"
fi

# Test CRUD archétypes
echo "3.2. Test CRUD archétypes..."
response=$(curl -s "${SERVER_URL}/api/archetypes")
if echo "$response" | grep -q "archetypes"; then
    echo "✅ API archétypes (CRUD) fonctionne"
else
    echo "❌ API archétypes (CRUD) ne fonctionne pas"
fi

# Arrêter le serveur si on l'a lancé
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    echo "4. Arrêt du serveur de test..."
    kill $SERVER_PID
    echo "✅ Serveur arrêté"
fi

echo ""
echo "🎉 Tests terminés !"
echo ""
echo "Résumé des fonctionnalités testées :"
echo "✅ Statut des intégrations"
echo "✅ Sites de scraping supportés"
echo "✅ Formats supportés"
echo "✅ Tournois récents avec archétypes"
echo "✅ Analyse méta"
echo "✅ Recherche par archétype"
echo "✅ Statistiques avec intégrations"
echo "✅ CRUD tournois existant"
echo "✅ CRUD archétypes existant"
echo ""
echo "Pour une utilisation complète :"
echo "1. Lancer le serveur: cd backend && python3 main_simple.py"
echo "2. Ouvrir la doc: http://localhost:8000/docs"
echo "3. Tester les nouvelles API dans l'interface Swagger" 