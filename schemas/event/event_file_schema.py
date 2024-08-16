from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from config import settings


class EventFileInput(BaseModel):
    splits_path: str = Field(max_length=200, default=f'{settings.aws.AWS_SPLITS_PATH}{str(uuid4())}.json')
    routes_path: str = Field(max_length=200, default=f'{settings.aws.AWS_ROUTES_PATH}{str(uuid4())}.json')
    results_path: str = Field(max_length=200, default=f'{settings.aws.AWS_RESULTS_PATH}{str(uuid4())}.json')
    event_id: UUID


class EventFileOutput(BaseModel):
    id: UUID
    splits_path: str
    routes_path: str
    results_path: str
    event_id: UUID

