#!/bin/bash

echo "🚀 Démarrage de Metalyzr"
echo "========================"

# Fonction pour nettoyer les processus au Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Arrêt de Metalyzr..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait
    echo "✅ Metalyzr arrêté"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Vérifier que nous sommes dans le bon dossier
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erreur: lancez ce script depuis la racine du projet Metalyzr"
    exit 1
fi

echo "🔧 Démarrage du backend..."
cd backend
source venv_new/bin/activate && python main_simple.py &
BACKEND_PID=$!
cd ..

echo "🎨 Démarrage du frontend..."
cd frontend/build
node serve-spa.js &
FRONTEND_PID=$!
cd ../..

# Attendre que les services démarrent
sleep 3

echo ""
echo "✅ Metalyzr est prêt !"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Attendre indéfiniment
wait 