from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from ..post.post import Post
    from ..article.article import Article
    from ..subscription.subscription import Subscription
    from ..team_member.team_member import TeamMember


class User(Base):
    first_name: Mapped[str] = mapped_column(String(20), unique=False)
    last_name: Mapped[str] = mapped_column(String(20), unique=False)
    hashed_password: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=sqlalchemy.sql.expression.true(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now(),
                                            onupdate=sqlalchemy.func.now(), server_default=sqlalchemy.func.now())
    email: Mapped[str] = mapped_column(String(40), unique=True, server_default='')

    # Relations
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete")
    team_members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="user", cascade="all, delete")
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="user",
                                                              cascade="all, delete")
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="author",
                                                     cascade="all, delete")
