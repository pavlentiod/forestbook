from typing import List

from fastapi import Security, Depends, APIRouter

from src.config import settings
from src.schemas.post.post_schema import PostPreview, PostFilter
from src.schemas.user.user_schema import UserPreview, UserUpdate
from src.services.auth.dependencies import get_current_active_user
from src.services.post.dependencies import get_post_service
from src.services.post.post_service import PostService
from src.services.user.dependencies import get_user_service
from src.services.user.user_service import UserService

router = APIRouter()
endpoints = settings.api.session


@router.get(
    endpoints.user.path,
    response_model=UserPreview,
)
async def read_current_user(
        user: UserPreview = Security(get_current_active_user, scopes=endpoints.user.security),
):
    """
    Get the current authenticated user's profile.

    Args:
        user (UserPreview): The currently authenticated user.

    Returns:
        UserPreview: The profile information of the authenticated user.
    """
    return user


@router.put(
    endpoints.user.path,
    response_model=UserPreview,
)
async def update_current_user(
        user_data: UserUpdate,
        user: UserPreview = Security(get_current_active_user, scopes=endpoints.user.security),
        user_service: UserService = Depends(get_user_service),
):
    """
    Update the current authenticated user's profile.

    Args:
        user_data (UserUpdate): The new data for the user's profile.
        user (UserPreview): The currently authenticated user.
        user_service (UserService): The service used to update the user data.

    Returns:
        UserPreview: The updated profile information of the authenticated user.
    """
    return await user_service.update(user.id, user_data)


@router.get(endpoints.posts.path,
            response_model=List[PostPreview])
async def user_posts(
        user: UserPreview = Security(get_current_active_user, scopes=endpoints.posts.security),
        post_service: PostService = Depends(get_post_service),
):
    id_filter = PostFilter(id=user.id)
    return await post_service.get_all(id_filter)
