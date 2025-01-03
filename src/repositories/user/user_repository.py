from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user.user import User
from src.schemas.user.user_schema import UserInput, UserOutput, UserFilter


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
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserOutput(**user.__dict__)

    async def get_all(self, user_filter: UserFilter) -> List[Optional[UserOutput]]:
        """
        Retrieve all users with optional filtering based on the UserFilter model.

        Args:
            user_filter (UserFilter): The filter criteria for retrieving users.

        Returns:
            List[UserOutput]: A list of users that match the filtering criteria.
        """
        # Prepare the base query
        stmt = select(User).order_by(User.id)

        # Create a list to hold the filter conditions
        filters = []

        # Dynamically add filters based on the user_filter values
        if user_filter.first_name:
            filters.append(User.first_name.ilike(f"%{user_filter.first_name}%"))  # Case-insensitive search
        if user_filter.last_name:
            filters.append(User.last_name.ilike(f"%{user_filter.last_name}%"))  # Case-insensitive search
        if user_filter.email:
            filters.append(User.email.ilike(f"%{user_filter.email}%"))  # Case-insensitive search
        if user_filter.is_active is not None:
            filters.append(User.is_active == user_filter.is_active)
        if user_filter.updated_from:
            filters.append(User.updated_at >= user_filter.updated_from)
        if user_filter.updated_to:
            filters.append(User.updated_at <= user_filter.updated_to)

        # Apply all filters at once (SQLAlchemy automatically uses AND between conditions)
        if filters:
            stmt = stmt.where(*filters)

        # Execute the query and fetch results
        result = await self.session.execute(stmt)
        entities = result.scalars().all()

        # Return the results as a list of UserOutput objects
        return [UserOutput(**user.__dict__) for user in entities]

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

    async def get_by_email(self, email: str):
        """
        Get user by email
        :param email: email string
        :return: UserOutput object
        """
        return await self.session.scalar(select(User).where(User.email == email))
        # return UserOutput(**user.__dict__)

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
