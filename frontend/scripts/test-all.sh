#!/bin/bash

echo "🧪 METALYZR - Suite de Tests Complète"
echo "====================================="

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Fonction pour logger
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "package.json" ]; then
    error "package.json non trouvé. Exécutez ce script depuis le dossier frontend/"
    exit 1
fi

log "Vérification de l'environnement de test..."

# Vérifier que Jest est installé
if ! npm list --depth=0 | grep -q "react-scripts"; then
    error "react-scripts non trouvé. Installation des dépendances..."
    npm install
fi

echo ""
echo "🔬 Phase 1: Tests Unitaires"
echo "========================="

# Tests du wrapper API
log "Test du wrapper API..."
((TOTAL_TESTS++))
if npm test -- --testPathPattern=apiWrapper.test.ts --watchAll=false --verbose; then
    success "Wrapper API: Tous les tests passés"
    TEST_RESULTS+=("✅ API Wrapper")
else
    error "Wrapper API: Échec des tests"
    TEST_RESULTS+=("❌ API Wrapper")
fi

# Tests du store Zustand
log "Test du store Zustand..."
((TOTAL_TESTS++))
if npm test -- --testPathPattern=adminStore.test.ts --watchAll=false --verbose; then
    success "Store Admin: Tous les tests passés"
    TEST_RESULTS+=("✅ Store Admin")
else
    error "Store Admin: Échec des tests"
    TEST_RESULTS+=("❌ Store Admin")
fi

# Tests du hook useAPIData
log "Test du hook useAPIData..."
((TOTAL_TESTS++))
if npm test -- --testPathPattern=useAPIData.test.tsx --watchAll=false --verbose; then
    success "Hook useAPIData: Tous les tests passés"
    TEST_RESULTS+=("✅ Hook useAPIData")
else
    error "Hook useAPIData: Échec des tests"
    TEST_RESULTS+=("❌ Hook useAPIData")
fi

echo ""
echo "🔗 Phase 2: Tests d'Intégration"
echo "==============================="

# Tests d'intégration du dashboard admin
log "Test d'intégration du dashboard admin..."
((TOTAL_TESTS++))
if npm test -- --testPathPattern=adminDashboard.integration.test.tsx --watchAll=false --verbose; then
    success "Dashboard Admin: Intégration réussie"
    TEST_RESULTS+=("✅ Dashboard Integration")
else
    error "Dashboard Admin: Échec de l'intégration"
    TEST_RESULTS+=("❌ Dashboard Integration")
fi

echo ""
echo "🏗️  Phase 3: Tests de Build"
echo "========================="

# Test de build
log "Test de construction de l'application..."
((TOTAL_TESTS++))
if npm run build > /dev/null 2>&1; then
    success "Build: Construction réussie"
    TEST_RESULTS+=("✅ Build Process")
else
    error "Build: Échec de la construction"
    TEST_RESULTS+=("❌ Build Process")
fi

# Vérifier la taille des bundles
if [ -d "build/static/js" ]; then
    JS_SIZE=$(du -sh build/static/js/*.js 2>/dev/null | awk '{sum += $1} END {print sum "K"}')
    CSS_SIZE=$(du -sh build/static/css/*.css 2>/dev/null | awk '{sum += $1} END {print sum "K"}')
    log "Taille des bundles: JS=${JS_SIZE}, CSS=${CSS_SIZE}"
fi

echo ""
echo "🌐 Phase 4: Tests Fonctionnels"
echo "=============================="

# Test de démarrage du serveur de développement
log "Test du serveur de développement..."
((TOTAL_TESTS++))

# Démarrer le serveur en arrière-plan
PORT=3001 BROWSER=none npm start > /dev/null 2>&1 &
SERVER_PID=$!
sleep 10

# Tester la connectivité
if curl -s -f http://localhost:3001 > /dev/null; then
    success "Serveur de dev: Démarrage réussi"
    TEST_RESULTS+=("✅ Dev Server")
else
    error "Serveur de dev: Échec du démarrage"
    TEST_RESULTS+=("❌ Dev Server")
fi

# Arrêter le serveur
kill $SERVER_PID 2>/dev/null

# Test du serveur Python (si le build existe)
if [ -f "build/simple-server.py" ]; then
    log "Test du serveur Python..."
    ((TOTAL_TESTS++))
    
    cd build
    python3 simple-server.py &
    PYTHON_PID=$!
    sleep 5
    
    if curl -s -f http://localhost:3000 > /dev/null; then
        success "Serveur Python: Démarrage réussi"
        TEST_RESULTS+=("✅ Python Server")
    else
        error "Serveur Python: Échec du démarrage"
        TEST_RESULTS+=("❌ Python Server")
    fi
    
    kill $PYTHON_PID 2>/dev/null
    cd ..
fi

echo ""
echo "🧪 Phase 5: Tests de l'API Mock"
echo "==============================="

# Tests des mocks
log "Test des handlers mock..."
((TOTAL_TESTS++))

cat << 'EOF' > /tmp/test-mock.js
const { mockHandlers, setupMockAPI } = require('./src/api/mockHandlers.ts');

// Test simple des mocks
const testMocks = () => {
    try {
        // Vérifier que les mocks sont définis
        if (!mockHandlers['/api/stats']) throw new Error('Mock stats manquant');
        if (!mockHandlers['/health']) throw new Error('Mock health manquant');
        
        // Vérifier la structure des données
        const stats = mockHandlers['/api/stats'];
        if (typeof stats.tournaments !== 'number') throw new Error('Stats tournaments invalide');
        
        console.log('✅ Mocks API: Validation réussie');
        process.exit(0);
    } catch (error) {
        console.log('❌ Mocks API: ' + error.message);
        process.exit(1);
    }
};

testMocks();
EOF

if node /tmp/test-mock.js 2>/dev/null; then
    success "Mocks API: Validation réussie"
    TEST_RESULTS+=("✅ API Mocks")
else
    error "Mocks API: Validation échouée"
    TEST_RESULTS+=("❌ API Mocks")
fi

rm -f /tmp/test-mock.js

echo ""
echo "🚀 Phase 6: Tests de Performance"
echo "==============================="

# Test de la taille des bundles
if [ -d "build" ]; then
    log "Analyse de la taille des bundles..."
    ((TOTAL_TESTS++))
    
    TOTAL_SIZE=$(du -sh build/ | awk '{print $1}')
    log "Taille totale du build: $TOTAL_SIZE"
    
    # Vérifier que le build n'est pas trop gros (< 50MB)
    SIZE_MB=$(du -sm build/ | awk '{print $1}')
    if [ "$SIZE_MB" -lt 50 ]; then
        success "Taille du build: Acceptable ($TOTAL_SIZE)"
        TEST_RESULTS+=("✅ Bundle Size")
    else
        warning "Taille du build: Importante ($TOTAL_SIZE)"
        TEST_RESULTS+=("⚠️  Bundle Size")
    fi
fi

echo ""
echo "📊 RÉSUMÉ DES TESTS"
echo "=================="

echo ""
echo "Résultats détaillés:"
for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo -e "Total: ${BLUE}$TOTAL_TESTS${NC} tests"
echo -e "Réussis: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Échoués: ${RED}$FAILED_TESTS${NC}"

PERCENT=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "Taux de réussite: ${BLUE}${PERCENT}%${NC}"

echo ""
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 TOUS LES TESTS SONT PASSÉS!${NC}"
    echo -e "${GREEN}✨ Votre application Metalyzr est prête pour la production${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  $FAILED_TESTS test(s) ont échoué${NC}"
    echo -e "${YELLOW}🔧 Veuillez corriger les problèmes avant de déployer${NC}"
    exit 1
fi 