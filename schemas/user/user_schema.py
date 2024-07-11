from pydantic import BaseModel, EmailStr, Field
from typing import List
from uuid import UUID

class UserInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)  # Assuming plain password is used for input
    access: int = Field(default=1)
    is_active: bool = Field(default=True)

class UserInDb(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    hashed_password: bytes
    access: int
    is_active: bool
    email: str

    class Config:
        orm_mode = True

class UserOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    access: int
    is_active: bool
    posts: List["PostOutput"]


