from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID

from schemas.post.post_schema import PostOutput


class GPSPostInput(BaseModel):
    lenght_s: int
    lenght_p: int
    climb: Optional[int]
    pace: int
    gpx_path: Optional[str] = Field(max_length=200)
    coord_data: Optional[Dict]

class GPSPostInDb(BaseModel):
    id: UUID
    lenght_s: int
    lenght_p: int
    climb: Optional[int]
    pace: int
    gpx_path: Optional[str]
    coord_data: Optional[Dict]
    post_id: int

    class Config:
        orm_mode = True

class GPSPostOutput(BaseModel):
    id: UUID
    lenght_s: int
    lenght_p: int
    climb: Optional[int]
    pace: int
    gpx_path: Optional[str]
    coord_data: Optional[Dict]
    post: PostOutput
