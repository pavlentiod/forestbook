from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.subscription.subscription_repository import SubscriptionRepository
from src.schemas.subscription.subscrption_schema import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanBase,
    SubscribeRequest,
    UserSubscriptionOut
)


class SubscriptionService:
    """
    Сервис для работы с подписками и тарифными планами:
    получение, создание, обновление, оформление подписки и т.д.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис подписок.

        :param session: Асинхронная сессия базы данных.
        """
        self.repository = SubscriptionRepository(session)

    # --- 🔓 Публичные методы ---

    async def get_all_plans(self) -> List[SubscriptionPlanBase]:
        """
        Получить список всех активных тарифных планов.

        :return: Список SubscriptionPlanBase
        """
        return await self.repository.get_all_plans()

    async def get_user_active_subscription(self, user_id: UUID) -> UserSubscriptionOut:
        """
        Получить текущую активную подписку пользователя.

        :param user_id: UUID пользователя
        :return: Текущая подписка
        :raises HTTPException: Если подписка отсутствует
        """
        sub = await self.repository.get_user_active_subscription(user_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Активная подписка не найдена")
        return sub

    async def subscribe(self, user_id: UUID, data: SubscribeRequest) -> UserSubscriptionOut:
        """
        Подписать пользователя на тарифный план.

        :param user_id: UUID пользователя
        :param data: Запрос на подписку
        :return: Созданная активная подписка
        :raises HTTPException: Если план не найден или возникла ошибка
        """
        plan = await self.repository.get_plan_by_id(data.plan_id)
        plan = SubscriptionPlanBase(**plan.__dict__)
        if not plan:
            raise HTTPException(status_code=404, detail="Тарифный план не найден")

        try:
            sub = await self.repository.create_subscription(user_id=user_id, data=data, plan=plan)
            return await self.get_user_active_subscription(user_id)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Ошибка при создании подписки")

    # --- 🔐 Админ-функции для управления планами ---

    async def create_plan(self, data: SubscriptionPlanCreate) -> SubscriptionPlanBase:
        """
        Создать новый тарифный план.

        :param data: Данные нового плана
        :return: Созданный план
        """
        return await self.repository.create_plan(data)

    async def update_plan(self, plan_id: UUID, data: SubscriptionPlanUpdate) -> SubscriptionPlanBase:
        """
        Обновить существующий тарифный план.

        :param plan_id: UUID плана
        :param data: Обновлённые данные
        :return: Обновлённый план
        :raises HTTPException: Если план не найден
        """
        plan = await self.repository.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Тарифный план не найден")

        return await self.repository.update_plan(plan, data)

    async def delete_plan(self, plan_id: UUID) -> bool:
        """
        Удалить тарифный план по ID.

        :param plan_id: UUID плана
        :return: True, если успешно
        :raises HTTPException: Если план не найден
        """
        plan = await self.repository.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Тарифный план не найден")

        return await self.repository.delete_plan(plan)
