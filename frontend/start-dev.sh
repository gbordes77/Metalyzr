#!/bin/bash

# Script de démarrage pour le frontend Metalyzr
# Résout les problèmes liés aux espaces dans le chemin

echo "🚀 Démarrage du frontend Metalyzr..."

# Exporter les variables d'environnement
export REACT_APP_API_URL=http://localhost:8000
export GENERATE_SOURCEMAP=false
export FAST_REFRESH=true

# Vérifier que node_modules existe
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules manquant, installation..."
    npm install
fi

# Vérifier que l'API backend est accessible
echo "🔍 Vérification de l'API backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API backend accessible"
else
    echo "❌ API backend non accessible. Assurez-vous que Docker est démarré:"
    echo "   docker-compose up -d"
    exit 1
fi

# Démarrer le serveur React
echo "🎯 Lancement du serveur React sur http://localhost:3000"
npx react-scripts start 