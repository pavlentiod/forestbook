from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db_helper
from src.services.user.user_service import UserService


async def get_user_service(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
) -> UserService:
    """
    Dependency to provide an instance of UserService with a scoped database session.
    This ensures that the UserService is correctly instantiated for each request and tied
    to the current database session.
    """
    return UserService(session)
