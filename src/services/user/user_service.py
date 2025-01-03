from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user.user_repository import UserRepository
from src.schemas.user.user_schema import UserInput, UserOutput, UserFilter, UserEndpoint
from .utils import hash_password
from ...database.models.user.user import User


class UserService:
    """
    Service class for handling users.
    """

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create(self, data: UserEndpoint) -> UserOutput:
        if await self.repository.user_exists_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        try:
            user = UserInput(**data.model_dump(exclude="password"), hashed_password=hash_password(data.password))
            return await self.repository.create(user)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Error creating user")

    async def get_all(self, user_filter: UserFilter) -> List[UserOutput]:
        return await self.repository.get_all(user_filter)

    async def get_user(self, _id: UUID4) -> User:
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_by_email(self, email: str) -> User:
        """
        Check exist and get user by email
        :param email: email string
        :return:
        """
        if not await self.repository.user_exists_by_email(email):
            raise HTTPException(status_code=404, detail="User not found")
        return await self.repository.get_by_email(email)


    # async def update(self, _id: UUID4, data: UserUpdate) -> UserOutput:
    #     user = await self.repository.get_by_id(_id)
    #     if not user:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     updated_user = await self.repository.update(user, data)
    #     return updated_user

    async def delete(self, _id: UUID4) -> bool:
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.repository.delete(user)
