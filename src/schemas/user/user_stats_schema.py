from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class UserStatsBase(BaseModel):
    total_posts: int
    gold: int
    silver: int
    bronze: int
    average_place: float
    best_place: Optional[int]
    total_time: int  # seconds
    total_distance: int  # meters
    average_backlog: float  # seconds
    average_backlog_percent: float  # percentage


class UserStatsCreate(UserStatsBase):
    user_id: UUID
    level: str


class UserStatsUpdate(BaseModel):
    total_posts: Optional[int] = None
    gold: Optional[int] = None
    silver: Optional[int] = None
    bronze: Optional[int] = None
    average_place: Optional[float] = None
    best_place: Optional[int] = None
    total_time: Optional[int] = None
    total_distance: Optional[int] = None
    average_backlog: Optional[float] = None
    average_backlog_percent: Optional[float] = None


class UserStatsResponse(UserStatsBase):
    user_id: UUID
    level: str

    class Config:
        from_attributes = True


class UserStatsInDB(BaseModel):
    user_id: UUID
    level: str

    total_posts: int = Field(ge=0)
    gold: int = Field(ge=0)
    silver: int = Field(ge=0)
    bronze: int = Field(ge=0)

    average_place: float = Field(ge=0.0)
    best_place: int | None = None

    total_time: int = Field(ge=0)  # in seconds
    total_distance: int = Field(ge=0)  # in meters

    average_backlog: float = Field(ge=0.0)  # in seconds
    average_backlog_percent: float = Field(ge=0.0)  # %

    class Config:
        from_attributes = True