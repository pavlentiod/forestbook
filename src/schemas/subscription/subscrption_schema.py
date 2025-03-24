from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional, List


# --- 📦 Тарифные планы --- #

class SubscriptionPlanBase(BaseModel):
    """
    Базовая схема тарифного плана (для вывода).
    """
    id: UUID4
    name: str
    description: Optional[str]
    price: float
    duration_days: int
    scopes: List[str]
    is_active: bool



class SubscriptionPlanCreate(BaseModel):
    """
    Схема для создания нового тарифного плана.
    """
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., ge=0)
    duration_days: int = Field(..., ge=1)
    scopes: List[str] = Field(default_factory=list)


class SubscriptionPlanUpdate(BaseModel):
    """
    Схема для обновления тарифного плана (частичная).
    """
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    price: Optional[float] = Field(None, ge=0)
    duration_days: Optional[int] = Field(None, ge=1)
    scopes: Optional[List[str]]
    is_active: Optional[bool]


# --- 👤 Подписки пользователей --- #

class SubscribeRequest(BaseModel):
    """
    Схема запроса на оформление подписки.
    """
    plan_id: UUID4
    external_id: Optional[str] = None  # Например, Stripe/RevenueCat ID


class UserSubscriptionOut(BaseModel):
    """
    Схема ответа с текущей активной подпиской пользователя.
    """
    plan: SubscriptionPlanBase
    start_date: datetime
    end_date: datetime
    is_active: bool

