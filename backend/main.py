from fastapi import FastAPI
from api.admin import routes as admin_routes

app = FastAPI(
    title="Metalyzr API",
    description="API for Magic: The Gathering Online metagame analysis.",
    version="0.1.0",
)

# Mount routers
app.include_router(admin_routes.router)

@app.get("/")
async def root():
    """
    Root endpoint providing a welcome message and API status.
    """
    return {"message": "Welcome to Metalyzr API", "status": "ok"} 