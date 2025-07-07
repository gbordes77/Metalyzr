import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost:5432/metalyzr"
)

# Création de l'engine
engine = create_engine(DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer toutes les tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Fonction pour supprimer toutes les tables (dev only)
def drop_tables():
    Base.metadata.drop_all(bind=engine) 