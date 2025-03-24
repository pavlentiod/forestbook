from typing import TYPE_CHECKING

from sqlalchemy import String, ARRAY
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base
if TYPE_CHECKING:
    from src.database.models.subscription.user_subscription import UserSubscription


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(nullable=False, default=0.0)
    duration_days: Mapped[int] = mapped_column(nullable=False, default=30)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")

    # Optional: подписки, связанные с этим планом
    subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="plan")
