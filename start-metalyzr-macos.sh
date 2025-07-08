#!/bin/bash

echo "🍎 Démarrage automatique de Metalyzr sur macOS..."
echo "================================================"

# Aller dans le dossier du projet
cd "/Users/guillaumebordes/Documents/Metalyzr "

# Vérifier qu'on est dans le bon dossier
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erreur : Dossiers backend/frontend non trouvés"
    echo "📍 Vérifiez que vous êtes dans le bon dossier"
    exit 1
fi

# Nettoyer les anciens processus
echo "🧹 Nettoyage des anciens processus..."
pkill -f "uvicorn.*main_simple" 2>/dev/null
pkill -f "python3.*main_simple" 2>/dev/null
pkill -f "node.*serve-spa" 2>/dev/null

# Attendre que les processus se terminent
sleep 2

# Créer le dossier logs s'il n'existe pas
mkdir -p logs

# Vérifier l'environnement virtuel
if [ ! -d "backend/venv_simple" ]; then
    echo "❌ Erreur : Environnement virtuel non trouvé"
    echo "🔧 Création de l'environnement virtuel..."
    cd backend
    python3 -m venv venv_simple
    source venv_simple/bin/activate
    pip install -r requirements_simple.txt
    cd ..
fi

# Vérifier le build frontend
if [ ! -d "frontend/build" ]; then
    echo "❌ Erreur : Build frontend non trouvé"
    echo "🔧 Construction du frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

echo "🚀 Démarrage du backend..."
# Démarrer backend
cd backend
source venv_simple/bin/activate
nohup python3 main_simple.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "⏳ Attente du démarrage backend (5 secondes)..."
sleep 5

# Vérifier que le backend est démarré
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend démarré avec succès (PID: $BACKEND_PID)"
else
    echo "❌ Erreur : Backend non accessible"
    echo "📋 Vérifiez les logs : tail -f logs/backend.log"
    exit 1
fi

echo "🌐 Démarrage du frontend..."
# Démarrer frontend
cd frontend/build
nohup node serve-spa.js > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "⏳ Attente du démarrage frontend (3 secondes)..."
sleep 3

# Vérifier que le frontend est démarré
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend démarré avec succès (PID: $FRONTEND_PID)"
else
    echo "❌ Erreur : Frontend non accessible"
    echo "📋 Vérifiez les logs : tail -f logs/frontend.log"
    exit 1
fi

echo ""
echo "🎉 Metalyzr démarré avec succès !"
echo "================================="
echo "✅ Backend PID: $BACKEND_PID"
echo "✅ Frontend PID: $FRONTEND_PID"
echo ""
echo "🔗 URLs d'accès :"
echo "   - 🌐 Frontend : http://localhost:3000"
echo "   - 🔧 Backend  : http://localhost:8000"
echo "   - 💚 Health   : http://localhost:8000/health"
echo ""
echo "📋 Commandes utiles :"
echo "   - Logs backend  : tail -f logs/backend.log"
echo "   - Logs frontend : tail -f logs/frontend.log"
echo "   - Arrêt propre  : pkill -f 'uvicorn.*main_simple' && pkill -f 'node.*serve-spa'"
echo ""
echo "🍎 Metalyzr est maintenant opérationnel sur macOS !" 