#!/bin/bash

echo "🔧 Démarrage du backend Metalyzr..."

# Vérifier que nous sommes dans le dossier backend
if [ ! -f "main_simple.py" ]; then
    echo "❌ Erreur: lancez ce script depuis le dossier backend/"
    exit 1
fi

# Activer l'environnement virtuel et démarrer
if [ -d "venv_new" ]; then
    source venv_new/bin/activate
elif [ -d "venv_simple" ]; then
    source venv_simple/bin/activate
else
    echo "❌ Erreur: aucun environnement virtuel trouvé"
    echo "💡 Exécutez: python3 -m venv venv_new && source venv_new/bin/activate && pip install -r requirements_simple.txt"
    exit 1
fi

echo "✅ Backend démarré sur http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "🏥 Health check: http://localhost:8000/health"
echo ""

python main_simple.py 