from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.repositories.user.user_stats_repository import UserStatsRepository
from src.schemas.user.user_stats_schema import UserStatsInDB, UserStatsUpdate
from src.services.redis_storage.redis_service import RedisStorage


class UserStatsService:
    """
    Сервис для управления статистикой пользователей с поддержкой кэширования.
    """

    def __init__(self, session: AsyncSession):
        self.repository = UserStatsRepository(session)
        self.redis = RedisStorage()
        self.redis_keys = settings.redis.user_stats

    async def get_all_by_user(self, user_id: UUID) -> List[UserStatsInDB]:
        """
        Получить всю статистику пользователя из кэша или БД.

        :param user_id: UUID пользователя
        :return: Список статистик по уровням
        """
        redis_key = self.redis_keys.many_by_user(str(user_id))
        try:
            if (cached := self.redis.get(redis_key)) is not None:
                return cached

            stats = await self.repository.get_all_by_user(user_id)
            self.redis.set(redis_key, stats, ex=self.redis_keys.GET_ALL_EX)
            return stats
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка при получении статистики пользователя")

    async def get_by_user_and_level(self, user_id: UUID, level: str) -> UserStatsInDB:
        """
        Получить статистику пользователя по уровню.

        :param user_id: UUID пользователя
        :param level: Уровень соревнований
        :return: Статистика по уровню
        :raises HTTPException: если не найдена
        """
        redis_key = self.redis_keys.key_by_user_and_level(str(user_id), level)
        try:
            if (cached := self.redis.get(redis_key)) is not None:
                return cached

            stats = await self.repository.get_by_user_and_level(user_id, level)
            if not stats:
                raise HTTPException(status_code=404, detail="Статистика не найдена")

            self.redis.set(redis_key, stats, ex=self.redis_keys.GET_ALL_EX)
            return stats
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка при получении статистики по уровню")

    async def update_or_create(self, user_id: UUID, level: str, data: UserStatsUpdate) -> UserStatsInDB:
        """
        Обновить или создать статистику по уровню соревнований, сбросив кэш.

        :param user_id: UUID пользователя
        :param level: Уровень соревнований
        :param data: Обновляемые поля
        :return: Обновленная или новая статистика
        """
        try:
            updated = await self.repository.create_or_update(user_id, level, data)

            # сбрасываем кэш
            self.redis.delete(self.redis_keys.key_by_user_and_level(str(user_id), level))
            self.redis.delete(self.redis_keys.many_by_user(str(user_id)))

            return updated
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Ошибка при обновлении статистики")
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка базы данных при обновлении статистики")

    async def delete(self, user_id: UUID, level: str) -> None:
        """
        Удалить статистику и сбросить кэш.
        """
        try:
            await self.repository.delete(user_id, level)
            self.redis.delete(self.redis_keys.key_by_user_and_level(str(user_id), level))
            self.redis.delete(self.redis_keys.many_by_user(str(user_id)))
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка при удалении статистики")