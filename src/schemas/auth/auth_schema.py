from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    scopes: list = []

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class UserSignIn(BaseModel):
    email: EmailStr = Field()
    password: str = Field()


