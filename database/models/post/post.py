import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
if TYPE_CHECKING:
    from ..event.event import Event
    from ..user.user import User
    from .gps_post import GPS_Post


class Post(Base):
    title: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    place: Mapped[int] = mapped_column(Integer, nullable=True)
    median_p_bk: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[int] = mapped_column(Integer, nullable=True)
    backlog: Mapped[int] = mapped_column(Integer, nullable=True)
    points_number: Mapped[int] = mapped_column(Integer, nullable=False)
    split_firsts: Mapped[int] = mapped_column(Integer, nullable=True)
    image_path: Mapped[str] = mapped_column(String(40), nullable=True)
    split: Mapped[dict] = mapped_column(JSON, nullable=False)
    index: Mapped[str] = mapped_column(String(50), nullable=True)
    body: Mapped[dict] = mapped_column(JSON, nullable=False, server_default='{}')
    created_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=True)
    event: Mapped["Event"] = relationship(back_populates="posts")

    gps: Mapped["GPS_Post"] = relationship(back_populates="post", cascade="all, delete")