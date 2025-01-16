from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, Json

# Schema for input data (creating a post)
from src.config import settings


class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None


class PostEndpoint(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None


class PostPreview(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None
    media: str = ""

class PostContent(BaseModel):
    title: str
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None
    media: str = ""
    body: Json[Any] = Field(Json[Any], description="Json content with user comments")



class PostInDB(BaseModel):
    id: UUID
    title: str
    body: dict
    user_id: UUID
    event_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None

    @property
    def media(self) -> str:
        return settings.aws.tree.post_folder(self.id)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    body: Optional[dict] = Field(None)
    event_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    status: Optional[str] = None
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
