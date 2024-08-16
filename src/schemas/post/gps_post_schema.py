from pydantic import BaseModel, Field
from typing import Optional, Dict, TYPE_CHECKING
from uuid import UUID



class GPSPostInput(BaseModel):
    lenght_s: int
    lenght_p: int
    climb: Optional[int]
    pace: int
    gpx_path: Optional[str] = Field(max_length=200)
    coord_data: Optional[Dict]
    post_id: UUID


class GPSPostOutput(BaseModel):
    id: UUID
    post_id: UUID
    lenght_s: int
    lenght_p: int
    climb: Optional[int]
    pace: int
    gpx_path: Optional[str]
    coord_data: Optional[Dict]
    post_id: UUID
