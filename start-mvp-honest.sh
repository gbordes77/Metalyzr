#!/bin/bash
# Script de démarrage MVP Metalyzr - Version honnête
# Pas de fake, juste ce qui fonctionne vraiment

set -e

echo "🧹 Metalyzr MVP - Version honnête et simple"
echo "=================================================="

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js non trouvé"
    exit 1
fi

# Nettoyer les processus existants
echo "🧹 Nettoyage des processus existants..."
pkill -f "python3 main_simple.py" 2>/dev/null || true
pkill -f "node.*server.js" 2>/dev/null || true

# Créer le dossier de données
echo "📁 Création du dossier de données..."
mkdir -p backend/data

# Démarrer le backend
echo "🚀 Démarrage du backend (port 8000)..."
cd backend
python3 main_simple.py &
BACKEND_PID=$!
echo "✅ Backend démarré (PID: $BACKEND_PID)"

# Attendre que le backend soit prêt
echo "⏳ Attente du backend..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend prêt"
        break
    fi
    sleep 1
done

# Démarrer le frontend
echo "🚀 Démarrage du frontend (port 3000)..."
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "✅ Frontend démarré (PID: $FRONTEND_PID)"

# Attendre que le frontend soit prêt
echo "⏳ Attente du frontend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend prêt"
        break
    fi
    sleep 1
done

# Afficher les informations
echo ""
echo "🎯 Metalyzr MVP - Système honnête opérationnel"
echo "=================================================="
echo "📊 Backend:   http://localhost:8000"
echo "📚 API docs:  http://localhost:8000/docs"
echo "💻 Frontend:  http://localhost:3000"
echo "💾 Données:   backend/data/ (JSON local)"
echo ""
echo "🔧 Fonctionnalités disponibles:"
echo "   - CRUD Tournois"
echo "   - CRUD Archétypes"
echo "   - Persistance JSON locale"
echo "   - API REST complète"
echo "   - Interface web"
echo ""
echo "💡 Saisie manuelle uniquement - Pas de fake data"
echo "🛑 Ctrl+C pour arrêter"

# Créer un fichier de PIDs pour le nettoyage
echo "BACKEND_PID=$BACKEND_PID" > .mvp_pids
echo "FRONTEND_PID=$FRONTEND_PID" >> .mvp_pids

# Attendre l'interruption
wait 