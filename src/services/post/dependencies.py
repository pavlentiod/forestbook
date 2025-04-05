from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.dependencies import get_forestlab_client
from src.clients.forestlab_client import ForestLabClient
from src.database import db_helper
from src.services.post.post_service import PostService


async def get_post_service(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        forestlab: ForestLabClient = Depends(get_forestlab_client)
) -> PostService:
    """
    Dependency to provide an instance of PostService with a scoped database session.
    This ensures that the PostService is correctly instantiated for each request and tied
    to the current database session.
    """
    return PostService(session, forestlab)
