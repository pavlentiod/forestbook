from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user.user import User
from src.repositories.user.utils import hash_password
from src.schemas.user.user_schema import UserInput, UserOutput


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserInput) -> UserOutput:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            access=data.access,
            is_active=data.is_active
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserOutput(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            access=user.access,
            is_active=user.is_active,
            posts=[]
        )

    async def get_all(self) -> List[Optional[UserOutput]]:
        stmt = select(User).order_by(User.last_name)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserOutput(**user.__dict__) for user in users]

    async def get_user(self, _id: UUID4) -> UserOutput:
        user = await self.session.get(User, _id)
        return UserOutput(**user.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[User]:
        return await self.session.get(User, _id)

    async def user_exists_by_id(self, _id: UUID4) -> bool:
        user = await self.session.get(User, _id)
        return user is not None

    async def user_exists_by_email(self, email: str) -> bool:
        user = await self.session.scalar(select(User).where(User.email == email))
        return user is not None

    async def update(self, user: User, data: UserInput) -> UserOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return UserOutput(**user.__dict__)

    async def delete(self, user: User) -> bool:
        await self.session.delete(user)
        await self.session.commit()
        return True


