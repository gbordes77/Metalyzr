from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from backend.database import db_client
from backend.services.metagame_service import MetagameService
from backend.api import metagame as metagame_api

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Initialization ---
app = FastAPI(
    title="Metalyzr API",
    description="API for Magic: The Gathering metagame analysis.",
    version="2.0.0"
)

# --- Service and Client Initialization ---
# Create a single instance of the database client and the service
# This instance will be shared across the application lifetime
metagame_service = MetagameService(database_client=db_client)

# --- Event Handlers ---
@app.on_event("startup")
def startup_event():
    logger.info("Application startup...")
    # Initialize the database schema if it doesn't exist
    db_client.init_db()
    logger.info("Database connection established and schema checked.")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutdown...")
    db_client.close()
    logger.info("Database connection closed.")

# --- API Routers ---
app.include_router(metagame_api.router, prefix="/api/metagame", tags=["Metagame Analysis"])

# --- Health Check ---
@app.get("/health", tags=["System"])
def health_check():
    """Basic health check to confirm the API is running."""
    return {"status": "ok"}

# --- Exception Handler ---
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    ) 