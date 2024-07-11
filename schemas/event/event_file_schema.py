from pydantic import BaseModel, Field
from uuid import UUID

from schemas.event.event_schema import EventOutput


class EventFileInput(BaseModel):
    splits_path: str = Field(max_length=200)
    routes_path: str = Field(max_length=200)
    results_path: str = Field(max_length=200)


class EventFileInDb(BaseModel):
    id: UUID
    splits_path: str
    routes_path: str
    results_path: str
    event_id: int

    class Config:
        orm_mode = True

class EventFileOutput(BaseModel):
    id: UUID
    splits_path: str
    routes_path: str
    results_path: str
    event: EventOutput

