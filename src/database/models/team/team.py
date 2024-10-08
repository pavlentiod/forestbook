from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy import String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base

if TYPE_CHECKING:
    from src.database.models.team_member.team_member import TeamMember


class Team(Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now())

    # Relations
    members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete")
