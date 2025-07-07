#!/bin/bash

echo "🚀 Démarrage simple du frontend Metalyzr..."

# Tuer les processus existants sur le port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Variables d'environnement
export REACT_APP_API_URL=http://localhost:8000
export PORT=3000
export HOST=0.0.0.0

# Vérifier que l'API backend est accessible
echo "🔍 Vérification de l'API backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API backend accessible"
else
    echo "❌ API backend non accessible. Démarrage de Docker..."
    cd .. && docker-compose up -d backend
    sleep 5
    cd frontend
fi

# Créer ou mettre à jour le package.json avec proxy
echo "📝 Configuration du proxy..."
npm config set proxy-url http://localhost:8000

# Démarrer React avec proxy
echo "🎯 Lancement du serveur React..."
npm start 