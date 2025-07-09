#!/bin/bash
# Script de démarrage Metalyzr MVP
echo "🚀 Démarrage Metalyzr MVP..."
cd /Users/guillaumebordes/Documents/MetalyzrClean/backend
source venv_metalyzr/bin/activate
echo "✅ Environnement virtuel activé"
echo "📊 Démarrage du serveur sur http://localhost:8000"
uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload

