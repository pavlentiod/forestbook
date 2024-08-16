import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user.user_schema import UserInput
from service.user.user_service import UserService


@pytest.fixture
def sample_user_data() -> UserInput:
    return UserInput(
        first_name="John",
        last_name="Doe",
        email="john22.doe@example.com",
        password="securepassword",
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


async def test_create_user(session: AsyncSession, sample_user_data: UserInput):
    service = UserService(session)

    # Create a new user
    created_user = await service.create(sample_user_data)

    # Verify the created user has the expected attributes
    assert created_user.email == sample_user_data.email
    assert created_user.first_name == sample_user_data.first_name

    # Try to create the same user again (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.create(sample_user_data)

    # Clean up by deleting the created user (if necessary)
    await service.delete(created_user.id)

async def test_get_all_users(session: AsyncSession):
    service = UserService(session)

    # Retrieve all users (expecting at least one)
    all_users = await service.get_all()
    assert len(all_users) > 0

    # Clean up by deleting all users (if necessary)
    for user in all_users:
        await service.delete(user.id)

async def test_get_user_by_id(session: AsyncSession, sample_user_data: UserInput):
    service = UserService(session)

    # Create a new user
    created_user = await service.create(sample_user_data)

    # Retrieve the user by ID
    retrieved_user = await service.get_user(created_user.id)

    # Verify the retrieved user matches the created user
    assert retrieved_user.email == sample_user_data.email

    # Try to retrieve a non-existent user (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.get_user("cddfa9b3-8f80-4950-90af-94f07e1897d4")  # Assuming 999999 is not a valid ID

    # Clean up by deleting the created user
    await service.delete(created_user.id)

async def test_update_user(session: AsyncSession, sample_user_data: UserInput, updated_user_data: UserInput):
    service = UserService(session)

    # Create a new user
    created_user = await service.create(sample_user_data)

    # Update the user's information
    updated_user = await service.update(created_user.id, updated_user_data)

    # Verify the updated user has the new attributes
    assert updated_user.email == updated_user_data.email
    assert updated_user.last_name == updated_user_data.last_name

    # Try to update a non-existent user (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.update("cddfa9b3-8f80-4950-90af-94f07e1897d4", updated_user_data)  # Assuming 999999 is not a valid ID

    # Clean up by deleting the created user
    await service.delete(created_user.id)

async def test_delete_user(session: AsyncSession, sample_user_data: UserInput):
    service = UserService(session)

    # Create a new user
    created_user = await service.create(sample_user_data)

    # Delete the user and verify
    result = await service.delete(created_user.id)
    assert result is True

    # Try to delete a non-existent user (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.delete("cddfa9b3-8f80-4950-90af-94f07e1897d4")  # Assuming 999999 is not a valid ID

    # Clean up by deleting the created user (if necessary)
    # Note: Depending on your implementation, the user might already be deleted in the previous step.
