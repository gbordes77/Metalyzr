import logging
from fastapi import FastAPI
from .database import engine, Base
from .api.v1.endpoints import metagame
from . import models

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables in the database on startup
# In a real production app, you'd use Alembic migrations for this.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Metalyzr API")

app.include_router(metagame.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metalyzr API"} 