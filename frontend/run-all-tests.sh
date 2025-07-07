#!/bin/bash

echo "🚀 METALYZR - Suite de Tests Complète et Validation"
echo "================================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Variables globales
TOTAL_PHASES=6
CURRENT_PHASE=0
OVERALL_SUCCESS=true

# Fonctions utilitaires
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    OVERALL_SUCCESS=false
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

start_phase() {
    ((CURRENT_PHASE++))
    echo ""
    echo -e "${PURPLE}📋 Phase $CURRENT_PHASE/$TOTAL_PHASES: $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Vérification de l'environnement
check_environment() {
    start_phase "Vérification de l'environnement"
    
    # Vérifier qu'on est dans le bon dossier
    if [ ! -f "package.json" ]; then
        error "package.json non trouvé. Exécutez depuis le dossier frontend/"
        exit 1
    fi
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js non installé"
        exit 1
    fi
    success "Node.js trouvé: $(node --version)"
    
    # Vérifier npm
    if ! command -v npm &> /dev/null; then
        error "npm non installé"
        exit 1
    fi
    success "npm trouvé: $(npm --version)"
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        warning "Python3 non trouvé - tests serveur Python ignorés"
    else
        success "Python3 trouvé: $(python3 --version)"
    fi
    
    # Vérifier les dépendances
    if [ ! -d "node_modules" ]; then
        log "Installation des dépendances npm..."
        npm install
    fi
    success "Dépendances npm présentes"
}

# Phase 1: Tests unitaires Jest
run_unit_tests() {
    start_phase "Tests Unitaires (Jest)"
    
    log "Exécution des tests unitaires..."
    
    # Tests du wrapper API
    if npm test -- --testPathPattern=apiWrapper.test.ts --watchAll=false --verbose --silent; then
        success "Tests API Wrapper réussis"
    else
        error "Tests API Wrapper échoués"
    fi
    
    # Tests du store
    if npm test -- --testPathPattern=adminStore.test.ts --watchAll=false --verbose --silent; then
        success "Tests Store Admin réussis"
    else
        error "Tests Store Admin échoués"
    fi
    
    # Tests du hook
    if npm test -- --testPathPattern=useAPIData.test.tsx --watchAll=false --verbose --silent; then
        success "Tests Hook useAPIData réussis"
    else
        error "Tests Hook useAPIData échoués"
    fi
}

# Phase 2: Tests d'intégration
run_integration_tests() {
    start_phase "Tests d'Intégration"
    
    log "Exécution des tests d'intégration..."
    
    if npm test -- --testPathPattern=integration --watchAll=false --verbose --silent; then
        success "Tests d'intégration réussis"
    else
        error "Tests d'intégration échoués"
    fi
}

# Phase 3: Build et validation
run_build_tests() {
    start_phase "Tests de Build"
    
    log "Construction de l'application..."
    
    if npm run build > build.log 2>&1; then
        success "Build réussi"
        
        # Vérifier la taille du build
        if [ -d "build" ]; then
            BUILD_SIZE=$(du -sh build/ | awk '{print $1}')
            success "Taille du build: $BUILD_SIZE"
            
            # Vérifier les fichiers essentiels
            if [ -f "build/index.html" ] && [ -f "build/static/js/"*.js ]; then
                success "Fichiers essentiels présents"
            else
                error "Fichiers essentiels manquants dans le build"
            fi
        fi
    else
        error "Build échoué"
        cat build.log
    fi
    
    rm -f build.log
}

# Phase 4: Tests du serveur
run_server_tests() {
    start_phase "Tests du Serveur"
    
    if [ ! -f "build/simple-server.py" ]; then
        warning "Serveur Python non trouvé - cette phase sera ignorée"
        return
    fi
    
    log "Démarrage du serveur Python en arrière-plan..."
    
    cd build
    python3 simple-server.py &
    SERVER_PID=$!
    cd ..
    
    # Attendre que le serveur démarre
    sleep 5
    
    # Tester la connectivité de base
    if curl -s -f http://localhost:3000 > /dev/null; then
        success "Serveur Python démarré avec succès"
        
        # Exécuter les tests de validation
        if command -v python3 &> /dev/null && python3 -c "import requests" 2>/dev/null; then
            log "Exécution des tests de validation du serveur..."
            if python3 validate-server.py; then
                success "Validation du serveur réussie"
            else
                error "Validation du serveur échouée"
            fi
        else
            warning "Module requests Python non disponible - tests détaillés ignorés"
        fi
    else
        error "Impossible de se connecter au serveur Python"
    fi
    
    # Arrêter le serveur
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null
        log "Serveur Python arrêté"
    fi
}

# Phase 5: Tests de coverage
run_coverage_tests() {
    start_phase "Analyse de Couverture"
    
    log "Génération du rapport de couverture..."
    
    if npm run test:coverage > coverage.log 2>&1; then
        success "Rapport de couverture généré"
        
        # Extraire les métriques de couverture
        if [ -f "coverage/lcov-report/index.html" ]; then
            success "Rapport HTML disponible: coverage/lcov-report/index.html"
        fi
        
        # Afficher un résumé
        grep -A 10 "All files" coverage.log | head -5 || true
        
    else
        error "Génération du rapport de couverture échouée"
        cat coverage.log
    fi
    
    rm -f coverage.log
}

# Phase 6: Tests manuels automatisés
run_automated_manual_tests() {
    start_phase "Tests Manuels Automatisés"
    
    info "Vérification de la checklist des tests manuels..."
    
    # Vérifier que les fichiers de test existent
    if [ -f "MANUAL_TESTS.md" ]; then
        success "Guide de tests manuels disponible"
    else
        warning "Guide de tests manuels manquant"
    fi
    
    if [ -f "test-admin.html" ] || [ -f "build/test-admin.html" ]; then
        success "Page de test automatique disponible"
    else
        warning "Page de test automatique manquante"
    fi
    
    # Compter les tests disponibles
    TEST_COUNT=$(find src/tests -name "*.test.*" 2>/dev/null | wc -l)
    success "$TEST_COUNT fichiers de test trouvés"
    
    info "Pour les tests manuels, consultez MANUAL_TESTS.md"
}

# Résumé final
show_summary() {
    echo ""
    echo "📊 RÉSUMÉ GLOBAL"
    echo "================"
    
    if [ "$OVERALL_SUCCESS" = true ]; then
        echo -e "${GREEN}🎉 TOUS LES TESTS AUTOMATIQUES SONT PASSÉS!${NC}"
        echo ""
        echo -e "${GREEN}✨ Votre application Metalyzr est validée${NC}"
        echo ""
        echo "🚀 Prochaines étapes:"
        echo "   1. Exécuter les tests manuels (voir MANUAL_TESTS.md)"
        echo "   2. Démarrer l'application: ./start-fixed.sh"
        echo "   3. Tester dans le navigateur:"
        echo "      - http://localhost:3000 (Dashboard)"
        echo "      - http://localhost:3000/admin (Admin)"
        echo "      - http://localhost:3000/test-admin.html (Tests)"
        echo ""
        echo -e "${BLUE}📚 Documentation disponible:${NC}"
        echo "   - QUICK_FIX_GUIDE.md : Guide technique"
        echo "   - MANUAL_TESTS.md : Tests manuels"
        echo "   - coverage/lcov-report/index.html : Couverture de code"
        
    else
        echo -e "${RED}❌ DES TESTS ONT ÉCHOUÉ${NC}"
        echo ""
        echo -e "${YELLOW}🔧 Actions recommandées:${NC}"
        echo "   1. Vérifier les erreurs ci-dessus"
        echo "   2. Corriger les problèmes identifiés"
        echo "   3. Relancer ce script"
        echo ""
        echo -e "${BLUE}💡 Aide au débogage:${NC}"
        echo "   - Vérifier les logs de build"
        echo "   - Consulter la documentation"
        echo "   - Tester les composants individuellement"
    fi
}

# Nettoyage
cleanup() {
    log "Nettoyage des processus temporaires..."
    
    # Tuer les serveurs qui pourraient encore tourner
    pkill -f "simple-server.py" 2>/dev/null || true
    pkill -f "react-scripts" 2>/dev/null || true
    
    # Nettoyer les fichiers temporaires
    rm -f build.log coverage.log test.log
    
    log "Nettoyage terminé"
}

# Handler de signal pour nettoyage
trap cleanup EXIT

# EXECUTION PRINCIPALE
main() {
    # Vérifier l'environnement
    check_environment
    
    # Exécuter toutes les phases
    run_unit_tests
    run_integration_tests  
    run_build_tests
    run_server_tests
    run_coverage_tests
    run_automated_manual_tests
    
    # Afficher le résumé
    show_summary
    
    # Code de sortie basé sur le succès global
    if [ "$OVERALL_SUCCESS" = true ]; then
        exit 0
    else
        exit 1
    fi
}

# Lancer le script principal
main "$@" 