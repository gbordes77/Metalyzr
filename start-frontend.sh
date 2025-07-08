#!/bin/bash
echo "🚀 Démarrage du frontend Metalyzr"
echo "📁 Répertoire: $(pwd)"

# Aller dans le répertoire build
cd "frontend/build" || {
    echo "❌ Erreur: Impossible d'accéder au répertoire frontend/build"
    exit 1
}

echo "📂 Fichiers disponibles:"
ls -la *.html 2>/dev/null || echo "❌ Aucun fichier HTML trouvé"

echo "🌐 Démarrage du serveur sur http://localhost:3001"
echo "📊 Dashboard: http://localhost:3001"
echo "👨‍💼 Admin: http://localhost:3001/admin"
echo "🔗 API Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Démarrer le serveur
python3 -c "
import http.server
import socketserver
import os

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/admin':
            self.path = '/index.html'
        return super().do_GET()

PORT = 3001
print(f'✅ Server running on http://localhost:{PORT}')
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    httpd.serve_forever()
" 