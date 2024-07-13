from pydantic import BaseModel, Field
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from uuid import UUID


from schemas.post.gps_post_schema import GPSPostOutput




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
    user_id: UUID
    event_id: UUID


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
    event_id: UUID = None
    user_id: UUID = None
    gps: Optional["GPSPostOutput"] = None

