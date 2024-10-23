




from fastapi import APIRouter, Depends
from typing import List

from src.routers.dependencies import get_user_service
from src.schemas.user.user_schema import UserOutput, UserFilter
from src.services.user.user_service import UserService

# Create a FastAPI router for user-related endpoints
user_router = APIRouter()

# Define a GET endpoint for retrieving users with filters
@user_router.get("/", response_model=List[UserOutput])
async def get_users(
        user_filter: UserFilter = Depends(),  # Use the Pydantic model for filters
        service: UserService = Depends(get_user_service)
) -> List[UserOutput]:
    """
    Get users with optional filters.

    Args:
        user_filter (UserFilter): The filter criteria for fetching users.
        service (UserService, optional): The UserService instance with the database session injected.

    Returns:
        List[UserOutput]: A list of filtered users.
    """
    return await service.get_all(user_filter=user_filter)
