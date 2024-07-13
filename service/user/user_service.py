from typing import List
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from repository.user.user_repository import UserRepository
from schemas.user.user_schema import UserInput, UserOutput
from repository.user.utils import hash_password


class UserService:
    """
    Service class for handling users.
    """

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create(self, data: UserInput) -> UserOutput:
        if await self.repository.user_exists_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        try:
            return await self.repository.create(data)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Error creating user")

    async def get_all(self) -> List[UserOutput]:
        return await self.repository.get_all()

    async def get_user(self, _id: UUID4) -> UserOutput:
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


    async def update(self, _id: UUID4, data: UserInput) -> UserOutput:
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await self.repository.update(user, data)
        return updated_user

    async def delete(self, _id: UUID4) -> bool:
        user = await self.repository.get_by_id(_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.repository.delete(user)
