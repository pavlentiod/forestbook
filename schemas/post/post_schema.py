from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

from schemas.event.event_schema import EventOutput
from schemas.post.gps_post_schema import GPSPostOutput
from schemas.user.user_schema import UserOutput


class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    place: Optional[int]
    median_p_bk: int
    result: Optional[int]
    backlog: Optional[int]
    points_number: int
    split_firsts: Optional[int]
    image_path: Optional[str] = Field(max_length=40)
    split: Dict
    index: Optional[str] = Field(max_length=50)
    body: Dict

class PostInDb(BaseModel):
    id: UUID
    title: str
    place: Optional[int]
    median_p_bk: int
    result: Optional[int]
    backlog: Optional[int]
    points_number: int
    split_firsts: Optional[int]
    image_path: Optional[str]
    split: Dict
    index: Optional[str]
    body: Dict
    created_date: datetime
    user_id: int
    event_id: Optional[int]

    class Config:
        orm_mode = True

class PostOutput(BaseModel):
    id: UUID
    title: str
    place: Optional[int]
    median_p_bk: int
    result: Optional[int]
    backlog: Optional[int]
    points_number: int
    split_firsts: Optional[int]
    image_path: Optional[str]
    split: Dict
    index: Optional[str]
    body: Dict
    created_date: datetime
    user: UserOutput
    event: EventOutput
    gps: Optional["GPSPostOutput"]
