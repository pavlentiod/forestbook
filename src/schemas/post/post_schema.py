from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# Schema for input data (creating a post)
class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(str)
    user_id: UUID
    event_id: UUID
    track_id: UUID = None

# Schema for output data (displaying a post)
class PostOutput(BaseModel):
    id: UUID
    title: str
    body: str
    user_id: UUID
    event_id: UUID
    track_id: UUID
    created_at: datetime

# Schema for endpoints (updating a post)
class PostEndpoint(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(str)
    event_id: UUID
    user_id: UUID
    track_id: UUID = None

