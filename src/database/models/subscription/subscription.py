import sqlalchemy
from sqlalchemy import INTEGER, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.database.models.user.user import User


class Subscription(Base):
    access: Mapped[float] = mapped_column(INTEGER, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now(), nullable=False)
    end_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relations
    user: Mapped[list["User"]] = relationship("User", back_populates="subscription")
