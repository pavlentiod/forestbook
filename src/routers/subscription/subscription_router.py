from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4

from src.config import settings
from src.schemas.subscription.subscrption_schema import (
    SubscriptionPlanOutput,
    SubscriptionPlanInput,
    SubscriptionPlanUpdate,
    SubscribeRequest,
    UserSubscriptionOutput,
)
from src.services.auth.dependencies import get_current_active_user
from src.services.subscription.dependencies import get_subscription_service
from src.services.subscription.subscription_service import SubscriptionService

router = APIRouter()
endpoints = settings.api.subscription


@router.get(
    endpoints.get_all_plans.path,
    response_model=List[SubscriptionPlanOutput],
    status_code=status.HTTP_200_OK,
    dependencies=[Security(get_current_active_user, scopes=endpoints.get_all_plans.security)],
)
async def get_all_plans(
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Получить список всех активных тарифных планов.
    """
    return await subscription_service.get_all_plans()



@router.post(
    endpoints.subscribe.path,
    response_model=UserSubscriptionOutput,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=endpoints.subscribe.security)],
)
async def subscribe(
        data: SubscribeRequest,
        current_user=Depends(get_current_active_user),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Оформить подписку на выбранный тарифный план.
    """
    return await subscription_service.subscribe(user_id=current_user.id, data=data)


@router.post(
    endpoints.create_plan.path,
    response_model=SubscriptionPlanOutput,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=endpoints.create_plan.security)],
)
async def create_plan(
        data: SubscriptionPlanInput,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Создать новый тарифный план (только для админа).
    """
    return await subscription_service.create_plan(data)


@router.put(
    endpoints.update_plan.path,
    response_model=SubscriptionPlanOutput,
    status_code=status.HTTP_200_OK,
    dependencies=[Security(get_current_active_user, scopes=endpoints.update_plan.security)],
)
async def update_plan(
        _id: UUID4,
        data: SubscriptionPlanUpdate,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Обновить существующий тарифный план (только для админа).
    """
    return await subscription_service.update_plan(plan_id=_id, data=data)


@router.delete(
    endpoints.delete_plan.path,
    response_model=bool,
    status_code=status.HTTP_200_OK,
    dependencies=[Security(get_current_active_user, scopes=endpoints.delete_plan.security)],
)
async def delete_plan(
        _id: UUID4,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
):
    """
    Удалить тарифный план (только для админа).
    """
    return await subscription_service.delete_plan(plan_id=_id)
