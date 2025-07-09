#!/bin/bash

echo "🔧 Installation des intégrations réelles Metalyzr"
echo "================================================"

# Vérifier si on est dans le bon répertoire
if [ ! -f "backend/main_simple.py" ]; then
    echo "❌ Erreur: Doit être exécuté depuis la racine du projet"
    exit 1
fi

# Installer les dépendances
echo "📦 Installation des dépendances Python..."
cd backend
pip install -r requirements_integrations.txt

if [ $? -eq 0 ]; then
    echo "✅ Dépendances installées avec succès"
else
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers de cache..."
mkdir -p cache/integrations/jiliac
mkdir -p cache/integrations/scraper
mkdir -p cache/integrations/archetype_formats
mkdir -p data/archetype_formats

# Créer les dossiers d'archétypes par défaut
echo "📁 Création des dossiers d'archétypes..."
mkdir -p cache/integrations/archetype_formats/Modern/archetypes
mkdir -p cache/integrations/archetype_formats/Modern/fallbacks
mkdir -p cache/integrations/archetype_formats/Standard/archetypes
mkdir -p cache/integrations/archetype_formats/Standard/fallbacks

echo "✅ Dossiers créés avec succès"

# Tester l'importation
echo "🧪 Test d'importation des modules..."
python3 -c "
try:
    import httpx
    import bs4
    print('✅ httpx et BeautifulSoup importés')
except ImportError as e:
    print(f'❌ Erreur d\'importation: {e}')
    exit(1)

try:
    from integrations.jiliac_cache import JiliacCacheClient
    from integrations.mtg_scraper import MTGScraper
    from integrations.badaro_archetype_engine import BadaroArchetypeEngine
    from integrations.integration_service import IntegrationService
    print('✅ Tous les modules d\'intégration importés')
except ImportError as e:
    print(f'❌ Erreur d\'importation des modules: {e}')
    exit(1)

print('✅ Intégrations prêtes à l\'emploi')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation terminée avec succès !"
    echo ""
    echo "Pour tester les intégrations :"
    echo "cd backend && python3 main_simple.py"
    echo ""
    echo "Les nouvelles API sont disponibles sur :"
    echo "- http://localhost:8000/api/integrations/status"
    echo "- http://localhost:8000/api/integrations/tournaments/recent"
    echo "- http://localhost:8000/api/integrations/scrape/deck"
    echo "- http://localhost:8000/api/integrations/meta/analysis"
    echo ""
    echo "Documentation complète : http://localhost:8000/docs"
else
    echo ""
    echo "❌ Erreur lors de l'installation"
    echo "Vérifiez que Python et pip sont installés"
    exit 1
fi 