#!/bin/bash

echo "🔧 METALYZR FRONTEND - Démarrage avec corrections"
echo "================================================="

# Variables d'environnement
export REACT_APP_API_URL=http://localhost:8000
export REACT_APP_USE_MOCKS=true
export HOST=localhost
export PORT=3000
export BROWSER=none

# Vérifier si on est dans le bon répertoire
if [ ! -f "package.json" ]; then
    echo "❌ Erreur: package.json non trouvé"
    echo "   Veuillez exécuter ce script depuis le dossier frontend/"
    exit 1
fi

echo "🧹 Nettoyage de l'environnement..."
rm -rf node_modules/.cache

echo "📦 Vérification des dépendances..."
if [ ! -d "node_modules" ] || [ ! -f "node_modules/zustand/package.json" ]; then
    echo "   Installation des dépendances manquantes..."
    npm install zustand
fi

echo "🔨 Construction de l'application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la construction"
    echo "   Tentative de nettoyage complet..."
    rm -rf node_modules package-lock.json
    npm install
    npm run build
    
    if [ $? -ne 0 ]; then
        echo "❌ Impossible de construire l'application"
        echo "   Utilisation du serveur Python de fallback..."
        cd build 2>/dev/null || {
            echo "❌ Aucun build disponible"
            exit 1
        }
        python3 simple-server.py
        exit 0
    fi
fi

echo "🚀 Démarrage du serveur..."

# Méthode 1: Serveur Python optimisé (recommandé)
if [ -f "build/simple-server.py" ]; then
    echo "   Utilisation du serveur Python avec proxy API"
    cd build
    python3 simple-server.py
else
    # Méthode 2: Serveur de développement React
    echo "   Utilisation du serveur de développement React"
    npm start
fi 