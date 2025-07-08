# 🎯 Test des Interfaces Metalyzr

## ✅ Prérequis

1. **Backend démarré** : `python backend/main_simple.py`
2. **Frontend construit** : `cd frontend && npm run build`

## 📊 Interface Utilisateur (Dashboard)

### Méthode 1 : Serveur HTTP simple
```bash
cd frontend/build
python3 -m http.server 3001
```
- **URL** : http://localhost:3001/index.html
- **Fonctionnalités** : Affichage des données, mais pas de proxy API

### Méthode 2 : Serveur avec proxy (recommandé)
```bash
cd frontend/build
python3 -c "
import http.server
import socketserver
import urllib.request
import json
import os

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/') or self.path == '/health':
            try:
                response = urllib.request.urlopen(f'http://localhost:8000{self.path}')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
            except:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{\"error\":\"Backend unavailable\"}')
        else:
            if self.path == '/': self.path = '/index.html'
            super().do_GET()

with socketserver.TCPServer(('', 3001), ProxyHandler) as httpd:
    print('🎯 Dashboard avec proxy: http://localhost:3001')
    httpd.serve_forever()
"
```

## 👨‍💼 Interface Admin

### Accès direct
- **URL** : http://localhost:3001/admin (avec le serveur proxy ci-dessus)

### Fonctionnalités testables

#### ✅ Affichage des données
1. **Statistiques** : Voir les totaux (tournois, archétypes, decks)
2. **Liste des tournois** : Tableau avec nom, format, participants, date
3. **Liste des archétypes** : Tableau avec nom, win rate, popularité

#### ✅ Ajout de données
1. **Nouveau tournoi** :
   - Nom : "Test Tournament"
   - Format : Standard/Modern/Legacy/Pioneer/Commander
   - Participants : 64
   - Date : Aujourd'hui

2. **Nouvel archétype** :
   - Nom : "Test Archetype"
   - Description : "Deck de test"
   - Win Rate : 55.5%
   - Popularité : 10.2%

#### ✅ Actualisation
- Bouton "Actualiser" pour recharger les données
- Lien "Dashboard" pour retourner à l'interface principale

## 🔧 Tests API directs

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Statistiques
```bash
curl http://localhost:8000/api/stats
```

### Ajouter un tournoi
```bash
curl -X POST http://localhost:8000/api/tournaments \
  -H "Content-Type: application/json" \
  -d '{"name": "Test API", "format": "Modern", "participants": 128}'
```

### Ajouter un archétype
```bash
curl -X POST http://localhost:8000/api/archetypes \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Deck", "description": "Deck via API", "winRate": 60.0, "popularity": 15.0}'
```

## 🎯 Scénarios de test

### Scénario 1 : Dashboard utilisateur
1. Accéder à http://localhost:3001/index.html
2. Vérifier l'affichage des statistiques
3. Voir la liste des tournois et archétypes
4. Tester le bouton "Actualiser"

### Scénario 2 : Panel admin
1. Accéder à http://localhost:3001/admin
2. Ajouter un nouveau tournoi via le formulaire
3. Ajouter un nouvel archétype via le formulaire
4. Vérifier que les données apparaissent dans les tableaux
5. Retourner au dashboard et voir les nouvelles données

### Scénario 3 : API directe
1. Utiliser curl pour ajouter des données
2. Actualiser l'interface pour voir les changements
3. Vérifier la cohérence des statistiques

## 🚨 Résolution de problèmes

### Backend ne répond pas
```bash
# Vérifier si le backend fonctionne
curl http://localhost:8000/health

# Redémarrer si nécessaire
cd backend
python3 main_simple.py
```

### Frontend ne charge pas
```bash
# Reconstruire le frontend
cd frontend
npm run build

# Servir avec Python
cd build
python3 -m http.server 3001
```

### Proxy API ne fonctionne pas
- Utiliser le serveur proxy Python ci-dessus
- Vérifier que le backend est sur le port 8000
- Regarder les logs de la console du navigateur

## 📈 Données de test

Le système contient déjà :
- **6 tournois** : Standard, Modern, Legacy
- **6 archétypes** : Mono-Red Aggro, Azorius Control, Simic Ramp
- **300 decks estimés**

Vous pouvez ajouter vos propres données via l'interface admin ou l'API.

---

🎉 **Interfaces prêtes à tester !** Utilisez les URLs ci-dessus pour explorer le MVP Metalyzr. 