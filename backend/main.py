import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright

from .database import engine, Base
from .api.v1.endpoints import metagame
from . import models

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables in the database on startup
# In a real production app, you'd use Alembic migrations for this.
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application startup...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        app.state.browser = browser
        print("Playwright browser launched and stored in app state.")
        yield
    # Shutdown
    print("Application shutdown...")
    await app.state.browser.close()
    print("Playwright browser closed.")

app = FastAPI(lifespan=lifespan)

app.include_router(metagame.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metalyzr API"} 