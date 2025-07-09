#!/bin/bash
# Script d'arrêt MVP Metalyzr - Version honnête

echo "🛑 Arrêt du MVP Metalyzr..."

# Lire les PIDs depuis le fichier
if [ -f .mvp_pids ]; then
    source .mvp_pids
    echo "🔍 PIDs trouvés: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
    
    # Arrêter les processus
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "✅ Backend arrêté"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✅ Frontend arrêté"
    fi
    
    rm .mvp_pids
else
    echo "⚠️ Fichier PIDs non trouvé, nettoyage par nom..."
    pkill -f "python3 main_simple.py" 2>/dev/null || true
    pkill -f "node.*server.js" 2>/dev/null || true
    echo "✅ Processus nettoyés"
fi

echo "🎯 MVP Metalyzr arrêté" 