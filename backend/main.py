from fastapi import FastAPI
from api.admin import routes as admin_routes
from api import tournaments, archetypes

app = FastAPI(
    title="Metalyzr API",
    description="API for Magic: The Gathering Online metagame analysis.",
    version="0.1.0",
)

# Mount routers
app.include_router(admin_routes.router)
app.include_router(tournaments.router)
app.include_router(archetypes.router)

@app.get("/")
async def root():
    """
    Root endpoint providing a welcome message and API status.
    """
    return {"message": "Welcome to Metalyzr API", "status": "ok"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy", "service": "metalyzr-api"} 