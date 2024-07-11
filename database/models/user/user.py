from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy.dialects.postgresql import BYTEA, INTEGER
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from ..post.post import Post


class User(Base):
    first_name: Mapped[str] = mapped_column(String(20), unique=False)
    last_name: Mapped[str] = mapped_column(String(20), unique=False)
    hashed_password: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    access: Mapped[int] = mapped_column(INTEGER, nullable=False, server_default="1", default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=sqlalchemy.sql.expression.true(), nullable=False)

    email: Mapped[str] = mapped_column(String(40), unique=True, server_default='')
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete")

