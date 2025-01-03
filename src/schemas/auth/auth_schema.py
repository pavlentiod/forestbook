from pydantic import BaseModel, EmailStr, Field


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserSignIn(BaseModel):
    email: EmailStr = Field()
    password: str = Field()


