from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from .event import Event


class Event_file(Base):
    splits_path : Mapped[str] = mapped_column(String(200), nullable=False)
    routes_path : Mapped[str] = mapped_column(String(200), nullable=False)
    results_path : Mapped[str] = mapped_column(String(200), nullable=False)


    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["Event"] = relationship(back_populates="event_files")

