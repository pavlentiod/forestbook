from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db_helper
from src.services.user.user_service import UserService


def get_user_service(session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> UserService:
    return UserService(session)