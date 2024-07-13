from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.event.event_file_schema import EventFileOutput


class EventInput(BaseModel):
    title: Optional[str] = Field(max_length=100, default='')
    count: int
    split_link: Optional[str] = Field(max_length=200)
    date: Optional[datetime]
    status: bool


class EventOutput(BaseModel):
    id: UUID
    title: Optional[str]
    count: int
    split_link: Optional[str]
    date: datetime
    status: bool
    event_files: Optional[EventFileOutput] = None

