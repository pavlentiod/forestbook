from fastapi import APIRouter

from src.routers.user.user import user_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=['Users'])

