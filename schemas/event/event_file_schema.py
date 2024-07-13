from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from uuid import UUID


class EventFileInput(BaseModel):
    splits_path: str = Field(max_length=200)
    routes_path: str = Field(max_length=200)
    results_path: str = Field(max_length=200)
    event_id: UUID


class EventFileOutput(BaseModel):
    id: UUID
    splits_path: str
    routes_path: str
    results_path: str
    event_id: UUID

