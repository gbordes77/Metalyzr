from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TournamentBase(BaseModel):
    uuid: str
    name: str
    format: Optional[str] = None
    source: str
    url: Optional[str] = None
    decks_count: Optional[int] = None

class TournamentCreate(TournamentBase):
    pass

class Tournament(TournamentBase):
    id: int
    date: Optional[str] = None # Keep as string to match model

    class Config:
        orm_mode = True 