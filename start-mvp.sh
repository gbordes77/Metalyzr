#!/bin/bash

echo "🎯 METALYZR MVP - Démarrage simple"
echo "=================================="

# Fonction pour tuer les processus existants
cleanup() {
    echo "🧹 Nettoyage des processus..."
    pkill -f "uvicorn" 2>/dev/null
    pkill -f "simple-server.py" 2>/dev/null
    pkill -f "main_simple" 2>/dev/null
    sleep 2
}

# Nettoyage initial
cleanup

# Démarrer le backend simple
echo "🚀 Démarrage du backend Python..."
cd backend
if [ ! -d "venv_simple" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv_simple
fi

source venv_simple/bin/activate
pip install -q -r requirements_simple.txt

echo "🔥 Backend démarré sur http://localhost:8000"
python main_simple.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du backend..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend prêt!"
        break
    fi
    echo "   Tentative $i/10..."
    sleep 2
done

# Initialiser les données d'exemple
echo "📊 Initialisation des données d'exemple..."
curl -s http://localhost:8000/api/init-sample-data > /dev/null

# Retourner au répertoire principal
cd ..

# Construire et démarrer le frontend
echo "🎨 Construction du frontend..."
cd frontend
npm install --silent
npm run build --silent

echo "🌐 Démarrage du serveur frontend sur http://localhost:3000"
cd build
python3 simple-server.py &
FRONTEND_PID=$!

cd ../..

echo ""
echo "🎉 MVP METALYZR DÉMARRÉ!"
echo "========================"
echo "🎯 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "📝 Pour arrêter: Ctrl+C puis ./stop-mvp.sh"
echo ""

# Attendre l'interruption
trap 'echo "🛑 Arrêt en cours..."; cleanup; exit 0' INT

# Boucle d'attente
while true; do
    sleep 1
done 