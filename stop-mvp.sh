#!/bin/bash

echo "🛑 ARRÊT MVP METALYZR"
echo "===================="

echo "🧹 Arrêt des processus..."

# Tuer tous les processus liés
pkill -f "uvicorn" 2>/dev/null
pkill -f "simple-server.py" 2>/dev/null  
pkill -f "main_simple" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null

echo "✅ Tous les processus arrêtés"
echo "💡 Pour redémarrer: ./start-mvp.sh" 