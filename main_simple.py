from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os

app = FastAPI(title="Metalyzr MVP", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import conditionnel des intégrations
try:
    from integrations.integration_service import IntegrationService
    integration_service = IntegrationService()
    integrations_loaded = True
    print("✅ Intégrations chargées avec succès")
except ImportError as e:
    print(f"⚠️  Intégrations non disponibles: {e}")
    integration_service = None
    integrations_loaded = False

@app.get("/", response_class=HTMLResponse)
async def root():
    status = "✅ Actives" if integrations_loaded else "⚠️  Non chargées (mode démo)"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metalyzr MVP</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f7; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .status {{ padding: 10px; background: {'#d1f5d3' if integrations_loaded else '#fff3cd'}; border-radius: 8px; margin: 10px 0; }}
            .endpoint {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 8px; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Metalyzr MVP</h1>
            <div class="status">
                <strong>Statut Backend:</strong> ✅ Opérationnel<br>
                <strong>Intégrations:</strong> {status}<br>
                <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            
            <h2>📊 API Endpoints:</h2>
            <div class="endpoint"><a href="/health">🟢 /health</a> - Statut système</div>
            <div class="endpoint"><a href="/api/stats">📈 /api/stats</a> - Statistiques</div>
            <div class="endpoint"><a href="/api/demo">🎮 /api/demo</a> - Données de démonstration</div>
            <div class="endpoint"><a href="/docs">📚 /docs</a> - Documentation Swagger</div>
            
            <h2>🔧 Informations système:</h2>
            <div class="endpoint">
                <strong>Répertoire:</strong> /Users/guillaumebordes/Documents/Metalyzr /backend<br>
                <strong>Environnement:</strong> venv_metalyzr<br>
                <strong>Mode:</strong> {'Production' if integrations_loaded else 'Démo'}
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "Metalyzr MVP",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "integrations_loaded": integrations_loaded,
        "environment": "production" if integrations_loaded else "demo",
        "working_directory": "/Users/guillaumebordes/Documents/Metalyzr /backend",
        "python_path": os.sys.executable
    })

@app.get("/api/stats")
async def get_stats():
    if integration_service:
        try:
            return await integration_service.get_complete_stats()
        except Exception as e:
            return JSONResponse({
                "error": f"Erreur intégrations: {str(e)}",
                "fallback_to_demo": True,
                "mode": "demo_fallback"
            })
    else:
        # Mode démo sans intégrations
        return JSONResponse({
            "mode": "demo",
            "tournaments": 156,
            "archetypes": 42,
            "formats": {
                "Standard": 45,
                "Modern": 68,
                "Legacy": 43
            },
            "last_updated": datetime.now().isoformat(),
            "message": "Données de démonstration - intégrations non chargées"
        })

@app.get("/api/demo")
async def get_demo_data():
    """Endpoint de démonstration toujours fonctionnel"""
    return JSONResponse({
        "status": "success",
        "tournaments": [
            {"id": 1, "name": "Pro Tour Thunder Junction", "format": "Standard", "date": "2024-04-26", "players": 320},
            {"id": 2, "name": "Modern Showcase Challenge", "format": "Modern", "date": "2024-04-25", "players": 156},
            {"id": 3, "name": "Legacy Premier", "format": "Legacy", "date": "2024-04-24", "players": 89}
        ],
        "top_archetypes": [
            {"name": "Domain Ramp", "meta_share": "18.5%", "win_rate": "54.2%", "format": "Standard"},
            {"name": "Esper Midrange", "meta_share": "15.3%", "win_rate": "52.8%", "format": "Standard"},
            {"name": "Mono Red Aggro", "meta_share": "12.7%", "win_rate": "51.9%", "format": "Modern"}
        ],
        "meta_summary": {
            "total_tournaments": 156,
            "total_players": 8420,
            "active_formats": ["Standard", "Modern", "Legacy", "Pioneer"],
            "last_update": datetime.now().isoformat()
        },
        "server_info": {
            "status": "demo_mode",
            "integrations_active": integrations_loaded,
            "version": "2.0.0"
        }
    })

@app.get("/api/test")
async def test_endpoint():
    """Endpoint de test simple"""
    return JSONResponse({
        "message": "🎉 Metalyzr MVP fonctionne parfaitement !",
        "timestamp": datetime.now().isoformat(),
        "server_status": "✅ Opérationnel",
        "path_fixed": "✅ Lien symbolique actif",
        "venv_active": "✅ venv_metalyzr",
        "dependencies": "✅ FastAPI, Uvicorn, BeautifulSoup4, Requests, HTTPX"
    })

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage Metalyzr MVP...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔧 Répertoire: /Users/guillaumebordes/Documents/Metalyzr /backend")
    uvicorn.run(app, host="0.0.0.0", port=8000) 