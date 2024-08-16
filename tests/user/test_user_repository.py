import random
import uuid

import bcrypt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user.user_repository import UserRepository
from schemas.user.user_schema import UserInput

def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


@pytest.fixture
def sample_user_data() -> UserInput:
    return UserInput(
        first_name="John2",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword222",
        access=1,
        is_active=True
    )

@pytest.fixture
def updated_user_data() -> UserInput:
    return UserInput(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        password="newsecurepassword",
        access=2,
        is_active=False
    )

async def test_create_user(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)

    assert created_user.id is not None
    assert created_user.first_name == sample_user_data.first_name
    assert created_user.last_name == sample_user_data.last_name
    assert created_user.email == sample_user_data.email
    assert created_user.access == sample_user_data.access
    assert created_user.is_active == sample_user_data.is_active

async def test_get_user(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    retrieved_user = await repository.get_user(created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.first_name == created_user.first_name
    assert retrieved_user.last_name == created_user.last_name
    assert retrieved_user.email == created_user.email
    assert retrieved_user.access == created_user.access
    assert retrieved_user.is_active == created_user.is_active

async def test_get_by_id(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    retrieved_user = await repository.get_by_id(created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.first_name == created_user.first_name
    assert retrieved_user.last_name == created_user.last_name
    assert retrieved_user.email == created_user.email
    assert retrieved_user.access == created_user.access
    assert retrieved_user.is_active == created_user.is_active

async def test_update_user(session: AsyncSession, sample_user_data, updated_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    retrieved_user = await repository.get_by_id(created_user.id)
    updated_user = await repository.update(retrieved_user, updated_user_data)

    assert updated_user.first_name == updated_user_data.first_name
    assert updated_user.last_name == updated_user_data.last_name
    assert updated_user.email == updated_user_data.email
    assert updated_user.access == updated_user_data.access
    assert updated_user.is_active == updated_user_data.is_active


async def test_delete_user(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    retrieved_user = await repository.get_by_id(created_user.id)
    deleted = await repository.delete(retrieved_user)

    assert deleted is True

async def test_user_exists_by_id(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    exists = await repository.user_exists_by_id(created_user.id)

    assert exists is True

async def test_get_all_users(session: AsyncSession, sample_user_data):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0,1000)) + sample_user_data.email
    await repository.create(sample_user_data)
    users = await repository.get_all()

    assert len(users) > 0


async def test_user_exists_by_email(session: AsyncSession, sample_user_data: dict):
    repository = UserRepository(session=session)
    sample_user_data.email = str(random.randint(0, 1000)) + sample_user_data.email
    created_user = await repository.create(sample_user_data)
    exists = await repository.user_exists_by_email(sample_user_data.email)
    assert exists is True

    # Check with a non-existing email
    non_existent_email = "nondhhexistent@example.com"
    exists = await repository.user_exists_by_email(non_existent_email)

    assert exists is False

