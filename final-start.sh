#!/bin/bash

echo "🎯 METALYZR - Démarrage complet de l'environnement"
echo "================================================"

# Répertoire de base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Fonction pour vérifier si un port est libre
check_port() {
    local port=$1
    if lsof -i:$port > /dev/null 2>&1; then
        echo "❌ Le port $port est déjà utilisé"
        return 1
    else
        echo "✅ Le port $port est libre"
        return 0
    fi
}

# Tuer les processus existants sur les ports
echo "🧹 Nettoyage des processus existants..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Démarrer l'infrastructure Docker (backend, DB, Redis)
echo "🐳 Démarrage de l'infrastructure Docker..."
docker-compose up -d backend postgres redis

# Attendre que l'API soit prête
echo "⏳ Attente que l'API backend soit prête..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API backend prête !"
        break
    fi
    echo "   Tentative $i/30..."
    sleep 2
done

# Vérifier si l'API est accessible
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Impossible d'accéder à l'API backend"
    echo "🔧 Vérifiez les logs: docker-compose logs backend"
    exit 1
fi

# Démarrer le frontend
echo "🎨 Démarrage du serveur frontend..."
cd frontend/build

# Créer un script Python avec CORS pour servir le frontend
cat > server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
from http.server import SimpleHTTPRequestHandler
import urllib.request
import json

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # Proxy pour l'API
        if self.path.startswith('/api/') or self.path.startswith('/health'):
            try:
                url = f'http://localhost:8000{self.path}'
                with urllib.request.urlopen(url) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(data)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
        
        # Servir les fichiers statiques
        super().do_GET()

if __name__ == "__main__":
    PORT = 3000
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"🚀 Serveur frontend démarré sur http://localhost:{PORT}")
        httpd.serve_forever()
EOF

python3 server.py &
FRONTEND_PID=$!

cd ../..

echo ""
echo "🎉 METALYZR DÉMARRÉ AVEC SUCCÈS !"
echo "=================================="
echo ""
echo "📍 URLs d'accès :"
echo "   🎯 Frontend Dashboard : http://localhost:3000"
echo "   👨‍💼 Admin Dashboard    : http://localhost:3000/admin" 
echo "   🔌 API Backend        : http://localhost:8000"
echo "   📚 API Documentation  : http://localhost:8000/docs"
echo ""
echo "🔍 Vérification des services :"
curl -s http://localhost:8000/health && echo "   ✅ Backend API : OK"
sleep 2
curl -s http://localhost:3000 > /dev/null && echo "   ✅ Frontend    : OK"
echo ""
echo "📊 Infrastructure Docker :"
docker-compose ps
echo ""
echo "⚡ Pour arrêter tous les services :"
echo "   kill $FRONTEND_PID && docker-compose down"
echo ""
echo "🎮 Le frontend est maintenant accessible à l'adresse :"
echo "   👉 http://localhost:3000"
echo ""

# Garder le script en cours d'exécution
wait $FRONTEND_PID 