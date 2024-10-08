from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user.user import User
from src.repositories.user.utils import hash_password
from src.schemas.user.user_schema import UserInput, UserOutput


class UserRepository:
    """
    Repository class for handling operations related to the User model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession instance to interact with the database.
        """
        self.session = session

    async def create(self, data: UserInput) -> UserOutput:
        """
        Creates a new user in the database.

        :param data: The input data to create a user.
        :return: The created user as UserOutput.
        """
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
            is_active=user.is_active
        )

    async def get_all(self) -> List[Optional[UserOutput]]:
        """
        Retrieves all users from the database, ordered by last name.

        :return: A list of UserOutput objects.
        """
        stmt = select(User).order_by(User.last_name)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserOutput(**user.__dict__) for user in users]

    async def get_user(self, _id: UUID4) -> UserOutput:
        """
        Retrieves a user by their ID.

        :param _id: The ID of the user to retrieve.
        :return: The user as UserOutput.
        """
        user = await self.session.get(User, _id)
        return UserOutput(**user.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[User]:
        """
        Retrieves a user by their ID. Returns None if the user doesn't exist.

        :param _id: The ID of the user to retrieve.
        :return: The user object or None if the user is not found.
        """
        return await self.session.get(User, _id)

    async def user_exists_by_id(self, _id: UUID4) -> bool:
        """
        Checks if a user exists in the database by their ID.

        :param _id: The ID of the user to check.
        :return: True if the user exists, otherwise False.
        """
        user = await self.session.get(User, _id)
        return user is not None

    async def user_exists_by_email(self, email: str) -> bool:
        """
        Checks if a user exists in the database by their email.

        :param email: The email of the user to check.
        :return: True if the user exists, otherwise False.
        """
        user = await self.session.scalar(select(User).where(User.email == email))
        return user is not None

    async def update(self, user: User, data: UserInput) -> UserOutput:
        """
        Updates the user with the given data.

        :param user: The user instance to update.
        :param data: The new data to update the user with.
        :return: The updated user as UserOutput.
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return UserOutput(**user.__dict__)

    async def delete(self, user: User) -> bool:
        """
        Deletes a user from the database.

        :param user: The user instance to delete.
        :return: True if the user was successfully deleted, otherwise False.
        """
        await self.session.delete(user)
        await self.session.commit()
        return True
