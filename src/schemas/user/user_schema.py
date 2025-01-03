from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID



class UserInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    hashed_password: bytes = Field()
    is_active: bool = Field(default=True)
    access: str = Field(default="1")



class UserOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    updated_at: datetime
    access: str


class UserEndpoint(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)


class UserFilter(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    updated_from: Optional[datetime] = None  # Filter users updated after this date
    updated_to: Optional[datetime] = None


class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None
    hashed_password: bytes = None
    is_active: bool = None
    access: str = None