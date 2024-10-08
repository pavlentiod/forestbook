import sqlalchemy
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.database.models.team.team import Team
from src.database.models.user.user import User


class TeamMember(Base):
    __tablename__ = "team_members"

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), nullable=False)
    joined_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=sqlalchemy.func.now())

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="team_members")
    team: Mapped["Team"] = relationship("Team", back_populates="members")
