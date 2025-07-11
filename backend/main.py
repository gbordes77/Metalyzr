import logging
from fastapi import FastAPI
from api.v1.endpoints import metagame
from database import init_db
import os

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Metalyzr API", version="1.0.0")

# Include the API router
# Note: The path to the router might need adjustment after full refactoring
app.include_router(metagame.router, prefix="/api/v1/metagame", tags=["Metagame Analysis"])

@app.on_event("startup")
def startup_event():
    """On startup, initialize the database."""
    logger.info("Metalyzr API starting up.")
    init_db()

@app.on_event("shutdown")
def shutdown_event():
    """On shutdown, log a message."""
    logger.info("Metalyzr API shutting down.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metalyzr API"} 