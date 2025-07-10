import logging
from fastapi import FastAPI
from api import metagame  # Corrected import path
import os

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Metalyzr API", version="1.0.0")

# Include the API router
app.include_router(metagame.router, prefix="/api/v1/metagame", tags=["Metagame Analysis"])

@app.on_event("startup")
async def startup_event():
    logger.info("Metalyzr API starting up.")

@app.on_event("shutdown")
def shutdown_event():
    metagame.db_client.close()  # Ensure the connection pool is closed gracefully
    logger.info("Metalyzr API shutting down.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metalyzr API"} 