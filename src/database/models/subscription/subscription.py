from uuid import UUID

import sqlalchemy
from sqlalchemy import INTEGER, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as UUID_2
from src.database import Base
from src.database.models.user.user import User


class Subscription(Base):
    access: Mapped[float] = mapped_column(INTEGER, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now(), nullable=False)
    end_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relations
    user_id: Mapped[UUID_2] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="subscription")
