from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# Schema for input data (creating a team)
class TeamInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=255, default=None)
    owner_id: UUID = Field(UUID)

# Schema for output data (displaying a team)
class TeamOutput(BaseModel):
    id: UUID
    name: str
    description: str
    owner_id: UUID
    created_at: datetime

# Schema for endpoints (updating a team)
class TeamEndpoint(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=255, default=None)
    owner_id: UUID = Field(UUID)
