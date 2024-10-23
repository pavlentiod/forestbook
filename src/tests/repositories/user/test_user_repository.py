import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user.user_repository import UserRepository
from src.schemas.user.user_schema import UserInput, UserOutput, UserUpdate
from src.database.models.user.user import User
from src.repositories.user.utils import exclude_password


@pytest.mark.anyio
class TestUserRepository:
    @pytest.fixture
    async def user_repo(self, session: AsyncSession):
        return UserRepository(session)

    @pytest.fixture
    async def create_user(self, user_repo: UserRepository):
        user_data = UserInput(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            password="securepassword"
        )
        return await user_repo.create(user_data)

    async def test_create_user(self, user_repo: UserRepository):
        """Test creating a new user."""
        user_data = UserInput(
            email="testuser2@example.com",
            first_name="Jane",
            last_name="Doe",
            password="securepassword"
        )
        user = await user_repo.create(user_data)

        assert user.id is not None
        assert user.email == user_data.email
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.hashed_password is not None  # Ensure password is hashed

    async def test_get_all_users(self, user_repo: UserRepository, create_user):
        """Test retrieving all users."""
        user = await create_user
        users = await user_repo.get_all()

        assert len(users) > 0
        assert users[0].id == user.id

    async def test_get_user_by_id(self, user_repo: UserRepository, create_user):
        """Test retrieving a user by their ID."""
        user = await create_user
        fetched_user = await user_repo.get_user(user.id)

        assert fetched_user.id == user.id
        assert fetched_user.email == user.email

    async def test_user_exists_by_id(self, user_repo: UserRepository, create_user):
        """Test checking if a user exists by their ID."""
        user = await create_user
        exists = await user_repo.user_exists_by_id(user.id)

        assert exists is True

    async def test_user_does_not_exist_by_id(self, user_repo: UserRepository):
        """Test checking if a user does not exist by a non-existing ID."""
        exists = await user_repo.user_exists_by_id(uuid4())

        assert exists is False

    async def test_user_exists_by_email(self, user_repo: UserRepository, create_user):
        """Test checking if a user exists by their email."""
        user = await create_user
        exists = await user_repo.user_exists_by_email(user.email)

        assert exists is True

    async def test_user_does_not_exist_by_email(self, user_repo: UserRepository):
        """Test checking if a user does not exist by a non-existing email."""
        exists = await user_repo.user_exists_by_email("nonexistentuser@example.com")

        assert exists is False

    async def test_update_user(self, user_repo: UserRepository, create_user):
        """Test updating user details."""
        user = await create_user
        update_data = UserUpdate(first_name="UpdatedFirstName")
        updated_user = await user_repo.update(user, update_data)

        assert updated_user.first_name == update_data.first_name

    async def test_delete_user(self, user_repo: UserRepository, create_user):
        """Test deleting a user."""
        user = await create_user
        deleted = await user_repo.delete(user)

        assert deleted is True
        assert await user_repo.user_exists_by_id(user.id) is False

    async def test_get_user_by_non_existing_id(self, user_repo: UserRepository):
        """Test retrieving a user by a non-existing ID."""
        user = await user_repo.get_user(uuid4())

        assert user is None
