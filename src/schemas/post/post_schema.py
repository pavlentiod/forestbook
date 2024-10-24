from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Schema for input data (creating a post)
class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    media: str = Field(min_length=1, max_length=100) # Just generate link to media folder in S3
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None

# Schema for output data (displaying a post)
class PostOutput(BaseModel):
    id: UUID
    title: str
    media: str
    body: dict
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None

# Schema for updating a post (PATCH/PUT endpoint)
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    media: Optional[str] = Field(None, min_length=1, max_length=100)
    body: Optional[dict] = Field(None)
    event_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class PostEndpoint(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None


class PostFilter(BaseModel):
    user_id: Optional[UUID] = None
    event_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    updated_at_from: Optional[datetime] = None
    updated_at_to: Optional[datetime] = None
