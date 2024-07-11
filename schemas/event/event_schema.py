from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from schemas.event.event_file_schema import EventFileOutput
from schemas.post.post_schema import PostOutput


class EventInput(BaseModel):
    title: Optional[str] = Field(max_length=100, default='')
    count: int
    split_link: Optional[str] = Field(max_length=200)
    date: Optional[datetime]
    status: bool

class EventInDb(BaseModel):
    id: UUID
    title: Optional[str]
    count: int
    split_link: Optional[str]
    date: datetime
    status: bool

    class Config:
        orm_mode = True

class EventOutput(BaseModel):
    id: UUID
    title: Optional[str]
    count: int
    split_link: Optional[str]
    date: datetime
    status: bool
    event_files: EventFileOutput
    posts: List["PostOutput"]

