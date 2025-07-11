from pydantic import BaseModel
from typing import List

class MetagameShare(BaseModel):
    archetype: str
    deck_count: int
    prevalence: float

    class Config:
        orm_mode = True

class MetagameResponse(BaseModel):
    data: List[MetagameShare]
    total_decks: int 