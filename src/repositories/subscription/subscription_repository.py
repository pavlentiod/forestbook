from datetime import datetime, timedelta, UTC
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import SubscriptionPlan
from src.database.models.subscription.user_subscription import UserSubscription
from src.schemas.subscription.subscrption_schema import (
    SubscriptionPlanOutput,
    SubscriptionPlanInput,
    SubscriptionPlanUpdate,
    UserSubscriptionOutput,
    SubscribeRequest
)


class SubscriptionRepository:
    """
    Репозиторий для управления подписками и тарифными планами.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация сессии базы данных.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    # -----------------------------
    # 📦 Методы для SubscriptionPlan
    # -----------------------------

    async def create_plan(self, data: SubscriptionPlanInput) -> SubscriptionPlanOutput:
        """
        Создание нового тарифного плана.

        :param data: Данные плана
        :return: Созданный план
        """
        plan = SubscriptionPlan(**data.model_dump())
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return SubscriptionPlanOutput(**plan.__dict__)

    async def get_all_plans(self) -> List[SubscriptionPlanOutput]:
        """
        Получение всех активных тарифных планов.

        :return: Список планов
        """
        query = select(SubscriptionPlan).where(SubscriptionPlan.is_active.is_(True))
        result = await self.session.execute(query)
        plans = result.scalars().all()
        return [SubscriptionPlanOutput(**p.__dict__) for p in plans]

    async def get_plan_by_id(self, plan_id: UUID) -> Optional[SubscriptionPlan]:
        stmt = (
            select(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id)
            .options(selectinload(SubscriptionPlan.subscriptions))  # загрузи связанные подписки
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_plan(self, plan: SubscriptionPlan, data: SubscriptionPlanUpdate) -> SubscriptionPlanOutput:
        """
        Обновление существующего плана.

        :param plan: Экземпляр плана
        :param data: Обновляемые данные
        :return: Обновлённый план
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(plan, key, value)
        await self.session.commit()
        await self.session.refresh(plan)
        return SubscriptionPlanOutput(**plan.__dict__)

    async def delete_plan(self, plan: SubscriptionPlan) -> bool:
        """
        Удаление тарифного плана.

        :param plan: План для удаления
        :return: True, если успешно
        """
        await self.session.delete(plan)
        await self.session.commit()
        return True

    # --------------------------------
    # 👤 Методы для подписок пользователя
    # --------------------------------

    async def get_user_active_subscription(self, user_id: UUID) -> Optional[UserSubscriptionOutput]:
        """
        Получение текущей активной подписки пользователя.

        :param user_id: UUID пользователя
        :return: Подписка или None
        """
        now = datetime.now(UTC)

        query = (
            select(UserSubscription)
            .options(selectinload(UserSubscription.plan))  # ← ключевая строка
            .where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.is_active.is_(True),
                    UserSubscription.start_date <= now,
                    UserSubscription.end_date >= now,
                )
            )
            .limit(1)
        )

        result = await self.session.execute(query)
        sub = result.scalars().first()

        if sub:
            return UserSubscriptionOutput(
                plan=SubscriptionPlanOutput.model_validate(sub.plan),  # ← безопасная конвертация
                start_date=sub.start_date,
                end_date=sub.end_date,
                is_active=sub.is_active,
            )

        return None

    async def create_subscription(
            self, user_id: UUID, data: SubscribeRequest, plan: SubscriptionPlanOutput
    ) -> UserSubscription:
        """
        Создание новой подписки для пользователя.

        :param user_id: UUID пользователя
        :param data: Данные подписки
        :param plan: Выбранный тарифный план
        :return: Созданная подписка
        """
        start = datetime.now(UTC)
        end = start + timedelta(days=plan.duration_days)
        sub = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            start_date=start,
            end_date=end,
            is_active=True,
            external_id=data.external_id
        )
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_user_subscriptions(self, user_id: UUID) -> Sequence[UserSubscription]:
        """
        Получение всех подписок пользователя (включая неактивные).

        :param user_id: UUID пользователя
        :return: Список подписок
        """
        query = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def deactivate_subscription(self, subscription: UserSubscription) -> bool:
        """
        Деактивация подписки (soft-off).

        :param subscription: Подписка для деактивации
        :return: True, если успешно
        """
        subscription.is_active = False
        await self.session.commit()
        return True

    async def delete_subscription(self, subscription: UserSubscription) -> bool:
        """
        Полное удаление подписки.

        :param subscription: Подписка для удаления
        :return: True, если успешно
        """
        await self.session.delete(subscription)
        await self.session.commit()
        return True
