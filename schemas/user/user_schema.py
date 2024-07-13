from pydantic import BaseModel, EmailStr, Field
from typing import List, TYPE_CHECKING, Optional
from uuid import UUID

# if TYPE_CHECKING:
from schemas.post.post_schema import PostOutput


class UserInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)  # Assuming plain password is used for input
    access: int = Field(default=1)
    is_active: bool = Field(default=True)


class UserOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    access: int
    is_active: bool
    posts: Optional[List[PostOutput]] = []


