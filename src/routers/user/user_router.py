from typing import List

from fastapi import APIRouter, Depends, status, Security
from pydantic import UUID4

from src.config import settings
from src.schemas.user.user_schema import UserEndpoint, UserPreview, UserFilter, UserUpdate
from src.services.auth.dependencies import get_current_active_user
from src.services.user.dependencies import get_user_service
from src.services.user.user_service import UserService

router = APIRouter()
endpoints = settings.api.user


@router.post(
    endpoints.create.path,
    response_model=UserPreview,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=endpoints.create.security)]
)
async def create(
        user_data: UserEndpoint,
        user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.

    Args:
        user_data (UserEndpoint): The user data required to create a new user.
        user_service (UserService): The service used to handle user-related operations.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        UserPreview: The newly created user object.
    """
    return await user_service.create(user_data)


@router.get(
    endpoints.get_all.path,
    response_model=List[UserPreview],
    dependencies=[Security(get_current_active_user, scopes=endpoints.get_all.security)]
)
async def get_all(
        user_filter: UserFilter = Depends(),
        user_service: UserService = Depends(get_user_service),
):
    """
    List all users with optional filtering.

    Args:
        user_filter (UserFilter): Optional filter parameters to refine the user list.
        user_service (UserService): The service used to retrieve users.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        List[UserOutput]: A list of users matching the filter criteria.
    """
    return await user_service.get_all(user_filter)


@router.get(
    endpoints.read.path,
    response_model=UserPreview,
    dependencies=[Security(get_current_active_user, scopes=endpoints.read.security)]
)
async def read(
        _id: UUID4,
        user_service: UserService = Depends(get_user_service),
):
    """
    Retrieve a user by their unique ID.

    Args:
        _id (UUID4): The unique identifier of the user to retrieve.
        user_service (UserService): The service used to fetch the user.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        UserPreview: The user object corresponding to the provided ID.
    """
    return await user_service.get_user(_id)


@router.get(
    endpoints.get_by_email.path,
    response_model=UserPreview,
    dependencies=[Security(get_current_active_user, scopes=endpoints.get_by_email.security)]
)
async def get_by_email(
        email: str,
        user_service: UserService = Depends(get_user_service),
):
    """
    Retrieve a user by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        user_service (UserService): The service used to fetch the user.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        UserPreview: The user object matching the provided email.
    """
    return await user_service.get_by_email(email)


@router.put(
    endpoints.update.path,
    response_model=UserPreview,
    dependencies=[Security(get_current_active_user, scopes=endpoints.update.security)]
)
async def update(
        _id: UUID4,
        user_data: UserUpdate,
        user_service: UserService = Depends(get_user_service),
):
    """
    Update a user's details.

    Args:
        _id (UUID4): The unique identifier of the user to update.
        user_data (UserUpdate): The new data to update the user with.
        user_service (UserService): The service used to perform the update.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        UserPreview: The updated user object.
    """
    return await user_service.update(_id, user_data)


@router.delete(
    endpoints.delete.path,
    response_model=bool,
    dependencies=[Security(get_current_active_user, scopes=endpoints.delete.security)]
)
async def delete(
        _id: UUID4,
        user_service: UserService = Depends(get_user_service),
):
    """
    Delete a user by their unique ID.

    Args:
        _id (UUID4): The unique identifier of the user to delete.
        user_service (UserService): The service used to delete the user.
        user (UserPreview): The currently authenticated user, required for authorization.

    Returns:
        bool: True if the user was successfully deleted, False otherwise.
    """
    return await user_service.delete(_id)



