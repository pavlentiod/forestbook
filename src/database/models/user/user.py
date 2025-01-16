from typing import TYPE_CHECKING, List

import sqlalchemy
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.post.post import Post


class User(Base):
    first_name: Mapped[str] = mapped_column(String(20), unique=False)
    last_name: Mapped[str] = mapped_column(String(20), unique=False)
    hashed_password: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=sqlalchemy.sql.expression.true(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now(),
                                            onupdate=sqlalchemy.func.now(), server_default=sqlalchemy.func.now())
    email: Mapped[str] = mapped_column(String(40), unique=True, server_default='')

    # Relations
    posts: Mapped[List["Post"]] = relationship(back_populates="runner", cascade="all, delete")
