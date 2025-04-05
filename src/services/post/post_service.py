from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.forestlab_client import ForestLabClient
from src.config import settings
from src.repositories.post.post_repository import PostRepository
from src.schemas.post.post_schema import PostInput, PostInDB, PostEndpoint, PostFilter, PostUpdate, PostExtendedResponse
from src.services.post.aggregator import PostAggregator
from src.services.redis_storage.redis_service import RedisStorage


class PostService:
    """
    Service class for managing post-related operations, including creation, retrieval,
    updates, and deletion, with Redis caching support.
    """

    def __init__(self, session: AsyncSession, forestlab: ForestLabClient):
        """
        Initializes the PostService with a database session and Redis client.

        :param session: Asynchronous database session.
        """
        self.repository = PostRepository(session)
        self.forestlab = forestlab
        self.redis_client = RedisStorage()
        self.redis_keys = settings.redis.post

    async def create(self, data: PostEndpoint) -> PostInDB:
        """
        Creates a new post and clears related cache.

        :param data: PostEndpoint containing post details.
        :return: Created post as PostInDB schema.
        :raises HTTPException: If an error occurs during post creation.
        """
        try:
            post = PostInput(**data.model_dump())
            created_post = await self.repository.create(post)

            # Clear cache for all posts
            redis_key_all = self.redis_keys.many()
            self.redis_client.delete(redis_key_all)
            return created_post
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Error creating post")

    async def get_all(self, filters: PostFilter) -> List[PostInDB]:
        """
        Retrieves all posts, optionally filtered, from cache or database.

        :param filters: PostFilter criteria for retrieving posts.
        :return: List of PostInDB schemas.
        """
        redis_key = self.redis_keys.many(filters=filters)
        if (cached_posts := self.redis_client.get(redis_key)) is not None:
            return cached_posts

        posts = await self.repository.get_all(filters)
        self.redis_client.set(redis_key, posts, ex=self.redis_keys.GET_ALL_EX)
        return posts

    async def get_post(self, _id: UUID) -> PostInDB:
        """
        Retrieves a post by its ID from cache or database.

        :param _id: UUID of the post.
        :return: Retrieved post as PostInDB schema.
        :raises HTTPException: If post is not found.
        """
        redis_key = self.redis_keys.key_by_post_id(_id)
        if (cached_post := self.redis_client.get(redis_key)) is not None:
            return cached_post

        post = await self.repository.get_post(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        self.redis_client.set(redis_key, post)
        return post

    async def get_extended_post(self, _id: UUID) -> PostExtendedResponse:
        """
        Получает расширенную информацию о посте, включая результаты, сплиты и другую статистику.

        :param _id: UUID поста
        :return: PostExtendedResponse с агрегированными данными
        :raises HTTPException: если пост не найден
        """
        post = await self.repository.get_post(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        aggregator = PostAggregator(self.forestlab)
        return await aggregator.aggregate(post)

    async def update(self, _id: UUID, data: PostUpdate) -> PostInDB:
        """
        Updates a post and clears relevant cache.

        :param _id: UUID of the post.
        :param data: PostUpdate with updated post details.
        :return: Updated post as PostInDB schema.
        :raises HTTPException: If post is not found.
        """
        post = await self.repository.get_by_id(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        updated_post = await self.repository.update(post, data)

        # Invalidate cache for the updated post and the list of posts
        redis_key_post = self.redis_keys.key_by_post_id(_id)
        redis_key_all = self.redis_keys.many()
        self.redis_client.delete(redis_key_post)
        self.redis_client.delete(redis_key_all)
        return updated_post

    async def delete(self, _id: UUID) -> bool:
        """
        Deletes a post and clears relevant cache.

        :param _id: UUID of the post to delete.
        :return: True if deletion was successful, False otherwise.
        :raises HTTPException: If post is not found.
        """
        post = await self.repository.get_by_id(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        redis_key_post = self.redis_keys.key_by_post_id(_id)
        redis_key_all = self.redis_keys.many()
        self.redis_client.delete(redis_key_post)
        self.redis_client.delete(redis_key_all)
        return await self.repository.delete(post)
