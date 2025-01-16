from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4

from src.config import settings
from src.schemas.post.post_schema import PostEndpoint, PostPreview, PostFilter, PostUpdate
from src.services.auth.dependencies import get_current_active_user
from src.services.post.dependencies import get_post_service
from src.services.post.post_service import PostService

router = APIRouter()
endpoints = settings.api.post


@router.post(
    endpoints.create.path,
    response_model=PostPreview,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(get_current_active_user, scopes=endpoints.create.security)]
)
async def create(
        post_data: PostEndpoint,
        post_service: PostService = Depends(get_post_service),
):
    """
    Create a new post.

    Args:
        post_data (PostEndpoint): Data required to create the post.
        post_service (PostService): Service handling post-related operations.

    Returns:
        PostPreview: The newly created post object.
    """
    return await post_service.create(post_data)


@router.get(
    endpoints.get_all.path,
    response_model=List[PostPreview],
    dependencies=[Security(get_current_active_user, scopes=endpoints.get_all.security)]
)
async def get_all(
        post_filter: PostFilter = Depends(),
        post_service: PostService = Depends(get_post_service),
):
    """
    Retrieve a list of posts with optional filters.

    Args:
        post_filter (PostFilter): Filters for retrieving posts (e.g., date, category).
        post_service (PostService): Service handling post-related operations.

    Returns:
        List[PostPreview]: A list of posts matching the filters.
    """
    return await post_service.get_all(post_filter)


@router.get(
    endpoints.read.path,
    response_model=PostPreview,
    dependencies=[Security(get_current_active_user, scopes=endpoints.read.security)]
)
async def read(
        _id: UUID4,
        post_service: PostService = Depends(get_post_service),
):
    """
    Retrieve a specific post by its ID.

    Args:
        _id (UUID4): Unique identifier of the post.
        post_service (PostService): Service handling post-related operations.

    Returns:
        PostPreview: The post object corresponding to the given ID.
    """
    return await post_service.get_post(_id)


@router.put(
    endpoints.update.path,
    response_model=PostPreview,
    dependencies=[Security(get_current_active_user, scopes=endpoints.update.security)]
)
async def update(
        _id: UUID4,
        post_data: PostUpdate,
        post_service: PostService = Depends(get_post_service),
):
    """
    Update the details of an existing post.

    Args:
        _id (UUID4): Unique identifier of the post to update.
        post_data (PostUpdate): The updated data for the post.
        post_service (PostService): Service handling post-related operations.

    Returns:
        PostPreview: The updated post object.
    """
    return await post_service.update(_id, post_data)


@router.delete(
    endpoints.delete.path,
    response_model=bool,
    dependencies=[Security(get_current_active_user, scopes=endpoints.delete.security)]
)
async def delete(
        _id: UUID4,
        post_service: PostService = Depends(get_post_service),
):
    """
    Delete a specific post by its ID.

    Args:
        _id (UUID4): Unique identifier of the post to delete.
        post_service (PostService): Service handling post-related operations.

    Returns:
        bool: True if the post was successfully deleted, False otherwise.
    """
    return await post_service.delete(_id)