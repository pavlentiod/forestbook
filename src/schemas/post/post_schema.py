from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field



class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100, default='Post title')
    body: Dict = {}
    user_id: UUID
    event_id: UUID


class PostOutput(BaseModel):
    id: UUID
    title: str
    body: Dict
    created_date: datetime
    event_id: UUID = None
    user_id: UUID = None


class PostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    user_id: UUID
    event_id: UUID

