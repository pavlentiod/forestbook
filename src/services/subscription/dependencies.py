from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.services.subscription.subscription_service import SubscriptionService


async def get_subscription_service(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
) -> SubscriptionService:
    """
    Зависимость для получения экземпляра SubscriptionService с привязкой к scoped-сессии.
    Обеспечивает корректную инициализацию сервиса для каждого запроса.
    """
    return SubscriptionService(session)
