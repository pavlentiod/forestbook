from typing import Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user.user_stats import UserStats
from src.schemas.user.user_stats_schema import UserStatsInDB, UserStatsCreate, UserStatsUpdate


class UserStatsRepository:
    """
    Репозиторий для управления статистикой пользователей по уровням соревнований.
    Обеспечивает методы для получения, создания, обновления и удаления записей статистики.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с переданной сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    async def get_by_user_and_level(self, user_id: UUID, level: str) -> Optional[UserStatsInDB]:
        """
        Получить статистику пользователя по определённому уровню соревнований.

        :param user_id: Идентификатор пользователя
        :param level: Уровень соревнования (например, "national")
        :return: Объект UserStatsInDB или None
        """
        stmt = select(UserStats).where(
            UserStats.user_id == user_id,
            UserStats.level == level
        )
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        return UserStatsInDB.model_validate(instance) if instance else None

    async def get_all_by_user(self, user_id: UUID) -> list[UserStatsInDB]:
        """
        Получить всю статистику по пользователю для всех уровней соревнований.

        :param user_id: Идентификатор пользователя
        :return: Список записей UserStatsInDB
        """
        stmt = select(UserStats).where(UserStats.user_id == user_id)
        result = await self.session.execute(stmt)
        return [UserStatsInDB.model_validate(row) for row in result.scalars().all()]

    async def create(self, data: UserStatsCreate) -> UserStatsInDB:
        """
        Создать новую запись статистики.

        :param data: Данные для создания (UserStatsCreate)
        :return: Созданная запись UserStatsInDB
        """
        stats = UserStats(**data.model_dump())
        self.session.add(stats)
        await self.session.flush()
        return UserStatsInDB.model_validate(stats)

    async def update(self, user_id: UUID, level: str, data: UserStatsUpdate) -> UserStatsInDB:
        """
        Обновить существующую запись статистики по пользователю и уровню.

        :param user_id: Идентификатор пользователя
        :param level: Уровень соревнований
        :param data: Данные для обновления (UserStatsUpdate)
        :return: Обновлённая запись UserStatsInDB
        """
        stmt = (
            update(UserStats)
            .where(UserStats.user_id == user_id, UserStats.level == level)
            .values(**data.model_dump(exclude_unset=True))
            .returning(UserStats)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return UserStatsInDB.model_validate(result.scalar_one())

    async def delete(self, user_id: UUID, level: str) -> None:
        """
        Удалить статистику пользователя по уровню соревнований.

        :param user_id: Идентификатор пользователя
        :param level: Уровень соревнования
        """
        stmt = delete(UserStats).where(UserStats.user_id == user_id, UserStats.level == level)
        await self.session.execute(stmt)

    async def create_or_update(self, user_id: UUID, level: str, data: UserStatsUpdate) -> UserStatsInDB:
        """
        Создаёт или обновляет статистику пользователя по уровню соревнований.

        :param user_id: Идентификатор пользователя
        :param level: Уровень соревнований
        :param data: Данные для сохранения (UserStatsUpdate)
        :return: Объект UserStatsInDB
        """
        existing = await self.get_by_user_and_level(user_id, level)
        if existing:
            return await self.update(user_id, level, data)
        stats_create = UserStatsCreate(user_id=user_id, level=level, **data.model_dump(exclude_unset=True))
        return await self.create(stats_create)