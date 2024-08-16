from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
if TYPE_CHECKING:
    from .post import Post


class GPS_Post(Base):
    lenght_s: Mapped[int] = mapped_column(Integer, nullable=False)
    lenght_p: Mapped[int] = mapped_column(Integer, nullable=False)
    climb: Mapped[int] = mapped_column(Integer, nullable=True)
    pace: Mapped[int] = mapped_column(Integer, nullable=False)
    gpx_path: Mapped[str] = mapped_column(String(200), nullable=True)
    coord_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship(back_populates="gps")



