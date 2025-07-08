#!/bin/bash

echo "🎨 Démarrage du frontend Metalyzr..."

# Vérifier que nous sommes dans le dossier frontend
if [ ! -d "build" ]; then
    echo "❌ Erreur: dossier build/ non trouvé"
    echo "💡 Exécutez d'abord: npm run build"
    exit 1
fi

# Aller dans le dossier build et démarrer le serveur
cd build

# Vérifier que serve-spa.js existe
if [ ! -f "serve-spa.js" ]; then
    echo "❌ Erreur: serve-spa.js non trouvé dans build/"
    exit 1
fi

echo "✅ Frontend démarré sur http://localhost:3000"
echo "📊 Dashboard: http://localhost:3000"
echo "👨‍💼 Admin: http://localhost:3000/admin"
echo ""

node serve-spa.js 