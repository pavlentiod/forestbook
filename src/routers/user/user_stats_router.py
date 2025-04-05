from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from src.config import settings
from src.database import db_helper
from src.schemas.user.user_stats_schema import UserStatsUpdate, UserStatsInDB
from src.services.user.user_stats_service import UserStatsService

# Инициализация маршрутизатора для статистики пользователей
user_stats_router = APIRouter()
routes = settings.api.user_stats  # Используем маршруты, определенные в конфиге


def get_user_stats_service(session=Depends(db_helper.scoped_session_dependency)) -> UserStatsService:
    """
    Провайдер зависимости, возвращающий экземпляр сервиса статистики пользователя.
    """
    return UserStatsService(session)


@user_stats_router.get(
    path=routes.get_all.path,
    response_model=List[UserStatsInDB],
    status_code=status.HTTP_200_OK,
    summary="Получить всю статистику пользователя",
)
async def get_all_user_stats(
        user_id: UUID = Path(..., description="UUID пользователя"),
        service: UserStatsService = Depends(get_user_stats_service)
):
    """
    Получить список всех статистик пользователя по уровням соревнований.

    :param user_id: UUID пользователя
    :param service: Сервис статистики пользователя
    :return: Список объектов UserStatsInDB
    """
    return await service.get_all_by_user(user_id)


@user_stats_router.get(
    path=routes.get_by_level.path,
    response_model=UserStatsInDB,
    status_code=status.HTTP_200_OK,
    summary="Получить статистику пользователя по уровню"
)
async def get_stats_by_level(
        user_id: UUID = Path(..., description="UUID пользователя"),
        level: str = Path(..., description="Уровень соревнований"),
        service: UserStatsService = Depends(get_user_stats_service)
):
    """
    Получить статистику пользователя на конкретном уровне соревнований.

    :param user_id: UUID пользователя
    :param level: Уровень (например, "national", "regional")
    :param service: Сервис статистики пользователя
    :return: Объект UserStatsInDB
    """
    return await service.get_by_user_and_level(user_id, level)


@user_stats_router.put(
    path=routes.update_or_create.path,
    response_model=UserStatsInDB,
    status_code=status.HTTP_200_OK,
    summary="Обновить или создать статистику по уровню"
)
async def update_or_create_stats(
        user_id: UUID = Path(..., description="UUID пользователя"),
        level: str = Path(..., description="Уровень соревнований"),
        update: UserStatsUpdate = Depends(),
        service: UserStatsService = Depends(get_user_stats_service)
):
    """
    Обновить существующую или создать новую статистику по уровню соревнований.

    :param user_id: UUID пользователя
    :param level: Уровень соревнований
    :param update: Объект с полями для обновления
    :param service: Сервис статистики пользователя
    :return: Объект UserStatsInDB
    """
    return await service.update_or_create(user_id, level, update)


@user_stats_router.delete(
    path=routes.delete.path,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить статистику по уровню"
)
async def delete_stats(
        user_id: UUID = Path(..., description="UUID пользователя"),
        level: str = Path(..., description="Уровень соревнований"),
        service: UserStatsService = Depends(get_user_stats_service)
):
    """
    Удалить статистику пользователя по конкретному уровню.

    :param user_id: UUID пользователя
    :param level: Уровень соревнований
    :param service: Сервис статистики пользователя
    :return: None
    """
    await service.delete(user_id, level)
