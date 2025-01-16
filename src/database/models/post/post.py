import datetime
from typing import TYPE_CHECKING
from uuid import UUID as UUID_2

import sqlalchemy
from sqlalchemy import String, JSON, DateTime, func, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


if TYPE_CHECKING:
    from src.database.models.user.user import User

class Post(Base):
    title: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    body: Mapped[dict] = mapped_column(JSON, nullable=False, server_default='{}')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now(),
                                            onupdate=sqlalchemy.func.now(), server_default=sqlalchemy.func.now())
    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    runner: Mapped["User"] = relationship(back_populates="posts")

    # ForestLab relations
    event_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    track_id: Mapped[UUID] = mapped_column(UUID, nullable=True)

    # Additional fields
    status: Mapped[str] = mapped_column(String(20), nullable=False,
                                        server_default='DRAFT')  # Status (DRAFT, PUBLISHED, ARCHIVED)
    # Optional fields
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)  # Array of tags

