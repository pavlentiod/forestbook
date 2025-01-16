from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.config import settings


class UserInput(BaseModel):
    first_name: str = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)
    email: EmailStr
    hashed_password: bytes = Field()
    is_active: bool = Field(default=True)


class UserPreview(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    updated_at: datetime
    urls: dict


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    updated_at: datetime
    hashed_password: bytes

    @property
    def urls(self) -> dict:
        tree = settings.aws.tree
        # TODO: define S3 files extension and name format
        urls = {
            "profile_photo": tree.user_folder(self.id) + "profile_photo.jpg"
        }
        return urls


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
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None


class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None
    password: str = None
    is_active: bool = None


