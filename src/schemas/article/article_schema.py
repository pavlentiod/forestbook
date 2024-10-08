from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# Schema for input data (creating an article)
class ArticleInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    author_id: UUID = Field(UUID)

# Schema for output data (displaying an article)
class ArticleOutput(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime

# Schema for endpoints (updating an article)
class ArticleEndpoint(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    author_id: UUID = Field(UUID)
