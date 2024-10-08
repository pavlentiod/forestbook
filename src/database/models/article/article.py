import sqlalchemy
from sqlalchemy import String, TEXT, ForeignKey, DATETIME, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.database.models.user.user import User


class Article(Base):

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now())

    # Relations
    author: Mapped["User"] = relationship("User", back_populates="articles")
