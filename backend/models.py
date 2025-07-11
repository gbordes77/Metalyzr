from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Tournament(Base):
    """
    SQLAlchemy model for a tournament.
    """
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    # Storing date as string for simplicity, as we get it in ISO format.
    # For complex queries, DateTime would be better.
    date = Column(String) 
    format = Column(String)
    source = Column(String)
    url = Column(String, nullable=True)
    decks_count = Column(Integer, nullable=True) 