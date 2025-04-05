import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
if TYPE_CHECKING:
    from src.database.models.subscription.subscription_plans import SubscriptionPlan
    from src.database.models.user.user import User


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="subscription")

    plan_id: Mapped[UUID] = mapped_column(ForeignKey("subscription_plans.id"))
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")

    start_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")
    external_id: Mapped[str] = mapped_column(String(100), nullable=True)  # Stripe / RevenueCat ID
