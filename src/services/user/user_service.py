from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user.user_repository import UserRepository
from src.schemas.user.user_schema import UserInput, UserFilter, UserEndpoint, UserInDB, UserUpdate
from .utils import hash_password
from ..redis_storage.redis_service import RedisStorage
from ...config import settings


class UserService:
    """
    Service class for managing user-related operations, including creating,
    retrieving, updating, and deleting users, with caching support.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the UserService with a database session and a Redis cache client.

        :param session: Asynchronous database session.
        :param redis_client: Instance of RedisStorage for caching user data.
        """
        self.repository = UserRepository(session)
        self.redis_client = RedisStorage()
        self.redis_keys = settings.redis.user

    async def create(self, data: UserEndpoint) -> UserInDB:
        """
        Creates a new user in the database.

        :param data: UserEndpoint schema containing user data.
        :return: The created user as a UserInDB schema.
        :raises HTTPException: If the email is already registered or other errors occur.
        """
        if await self.repository.user_exists_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        try:
            hashed_password = hash_password(data.password)
            user = UserInput(**data.model_dump(exclude={"password"}), hashed_password=hashed_password)
            user = await self.repository.create(user)

            # Redis
            redis_key = self.redis_keys.many()
            self.redis_client.delete(redis_key)

            return user
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Error creating user")

    async def get_all(self, user_filter: UserFilter) -> List[UserInDB]:
        """
        Retrieves all users, optionally filtered, from the database or cache.

        :param user_filter: Filters to apply when retrieving users.
        :return: A list of users as UserInDB schema.
        """

        # Redis
        redis_key = self.redis_keys.many(filters=user_filter)
        if (cached_users := self.redis_client.get(redis_key)) is not None:
            return cached_users

        users = await self.repository.get_all(user_filter)
        self.redis_client.set(redis_key, users, ex=self.redis_keys.GET_ALL_EX)  # Cache the user list
        return users

    async def get_user(self, _id: UUID4) -> UserInDB:
        """
        Retrieves a user by their ID.

        :param _id: User UUID.
        :return: The user as a UserInDB schema.
        :raises HTTPException: If the user is not found.
        """
        redis_key = self.redis_keys.key_by_user_id(_id)
        if (cached_user := self.redis_client.get(redis_key)) is not None:
            return cached_user

        user = await self.repository.get_user(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.redis_client.set(redis_key, user)  # Cache the user data
        return user

    async def get_by_email(self, email: str) -> UserInDB:
        """
        Retrieves a user by their email.

        :param email: User email address.
        :return: The user as a UserInDB schema.
        :raises HTTPException: If the user is not found.
        """
        redis_key = self.redis_keys.key_by_user_email(email)
        if (cached_user := self.redis_client.get(redis_key)) is not None:
            return cached_user

        if not await self.repository.user_exists_by_email(email):
            raise HTTPException(status_code=404, detail="User not found")

        user = await self.repository.get_by_email(email)
        self.redis_client.set(redis_key, user)  # Cache the user data
        return user

    async def update(self, _id: UUID4, data: UserUpdate) -> UserInDB:
        """
        Updates a user's data.

        :param _id: User UUID.
        :param data: UserUpdate schema containing updated user data.
        :return: The updated user as a UserInDB schema.
        :raises HTTPException: If the user is not found.
        """
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user
        updated_user = await self.repository.update(user, data)

        # Redis
        redis_key = self.redis_keys.key_by_user_id(_id)
        self.redis_client.delete(redis_key)  # Invalidate cache

        return updated_user

    async def delete(self, _id: UUID4) -> bool:
        """
        Deletes a user by their ID.

        :param _id: User UUID.
        :return: True if the user was deleted successfully, False otherwise.
        :raises HTTPException: If the user is not found.
        """
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Redis
        redis_key = self.redis_keys.key_by_user_id(_id)
        redis_key_all = self.redis_keys.many()
        self.redis_client.delete(redis_key)  # Invalidate cache
        self.redis_client.delete(redis_key_all)  # Invalidate cache

        return await self.repository.delete(user)
