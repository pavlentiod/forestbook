from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

from forestlab_schemas.event import EventResponse
from forestlab_schemas.runner import RunnerStat, RunnerLegStat, RunnerLegGEOStat, RunnerOutput
from pydantic import BaseModel, Field, Json

# Schema for input data (creating a post)
from src.config import settings
from src.schemas.user.user_schema import UserPreview


class PostInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    runner_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None


class PostEndpoint(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: dict = Field(default={})
    user_id: UUID
    event_id: UUID
    runner_id: UUID
    track_id: Optional[UUID] = None
    status: str = Field(default='DRAFT')
    tags: Optional[List[str]] = None


class PostPreview(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    event_id: UUID
    runner_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None
    media: str = ""

class PostContent(BaseModel):
    title: str
    user_id: UUID
    runner_id: UUID
    event_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None
    media: str = ""
    body: Json[Any] = Field(Json[Any], description="Json content with user comments")


class PostInDB(BaseModel):
    id: UUID
    title: str
    body: dict
    user_id: UUID
    event_id: UUID
    runner_id: UUID
    track_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    tags: Optional[List[str]] = None

    @property
    def media(self) -> str:
        return settings.aws.tree.post_folder(self.id)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    body: Optional[dict] = Field(None)
    event_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    runner_id: Optional[UUID] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class PostFilter(BaseModel):
    user_id: Optional[UUID] = None
    event_id: Optional[UUID] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    updated_at_from: Optional[datetime] = None
    updated_at_to: Optional[datetime] = None


class PostStats(BaseModel):
    """
    Расширенная статистика по посту.
    Включает как данные от ForestLab (например, сплиты, места),
    так и будущую аналитику ForestBook.
    """

    # runner_stat: Optional[RunnerStat] = None  # Данные по результату спортсмена
    # legs: Optional[List[LegOutput]] = None    # Общая информация по перегонкам

    # Пример будущих метрик, которые может считать ForestBook:
    speed_index: Optional[float] = None       # Индекс скорости по отношению к среднему
    mistake_score: Optional[int] = None       # Оценка ошибок на дистанции
    consistency_rating: Optional[float] = None  # Стабильность времени прохождения

    class Config:
        from_attributes = True

class PostExtendedResponse(BaseModel):
    id: UUID
    title: str
    tags: list[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    body: dict
    stats: RunnerStat
    info: RunnerOutput
    media: str = ""
