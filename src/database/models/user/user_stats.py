from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.database.base import Base
if TYPE_CHECKING:
    from src.database import User

class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="stats")

    level: Mapped[str] = mapped_column(String, primary_key=True)  # Пример: "national", "regional", "local"

    total_posts: Mapped[int] = mapped_column(Integer, default=0)

    gold: Mapped[int] = mapped_column(Integer, default=0)
    silver: Mapped[int] = mapped_column(Integer, default=0)
    bronze: Mapped[int] = mapped_column(Integer, default=0)

    average_place: Mapped[float] = mapped_column(Float, default=0.0)
    best_place: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_time: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    total_distance: Mapped[int] = mapped_column(Integer, default=0)  # meters

    average_backlog: Mapped[float] = mapped_column(Float, default=0.0)  # seconds
    average_backlog_percent: Mapped[float] = mapped_column(Float, default=0.0)  # e.g., 12.4 (%)

    def __repr__(self):
        return (
            f"<UserStatsByLevel user_id={self.user_id} level={self.level} "
            f"gold={self.gold} silver={self.silver} bronze={self.bronze}>"
        )
