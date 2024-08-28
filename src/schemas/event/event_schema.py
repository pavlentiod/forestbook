from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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


class EventEndpoint(BaseModel):
    title: Optional[str] = Field(max_length=100, default='')
    split_link: Optional[str] = Field(max_length=200)
    date: Optional[datetime]


class EventData(BaseModel):
    splits: dict
    routes: dict
    results: dict

