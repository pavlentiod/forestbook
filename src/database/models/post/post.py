import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, JSON, DateTime, func, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
if TYPE_CHECKING:
    from ..user.user import User


class Post(Base):
    title: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    body: Mapped[dict] = mapped_column(JSON, nullable=False, server_default='{}')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")

    # ForestLab relations
    event_id: Mapped[int] = mapped_column(UUID, nullable=False)
    track_id: Mapped[int] = mapped_column(UUID, nullable=True)

