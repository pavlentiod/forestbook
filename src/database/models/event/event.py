import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from ..post.post import Post


class Event(Base):
    title: Mapped[str] = mapped_column(String(100), nullable=True, server_default='', default='')
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    split_link: Mapped[str] = mapped_column(String(200), nullable=True, unique=False)
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now())
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)

    posts: Mapped[list["Post"]] = relationship(back_populates="event")
