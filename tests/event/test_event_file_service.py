import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from schemas.event.event_file_schema import EventFileInput
from service.event.event_file_service import EventFileService


@pytest.fixture
def sample_event_file_data() -> EventFileInput:
    return EventFileInput(
        splits_path="splits/sample.csv",
        routes_path="routes/sample.csv",
        results_path="results/sample.csv",
        event_id="e894c953-d404-4311-aea8-bc7098393157"
    )

@pytest.fixture
def updated_event_file_data() -> EventFileInput:
    return EventFileInput(
        splits_path="splits/updated.csv",
        routes_path="routes/updated.csv",
        results_path="results/updated.csv",
        event_id="e894c953-d404-4311-aea8-bc7098393157"
    )

async def test_create_event_file(session: AsyncSession, sample_event_file_data: EventFileInput):
    service = EventFileService(session)

    # Create a new event file
    created_event_file = await service.create(sample_event_file_data)

    # Verify the created event file has the expected attributes
    assert created_event_file.splits_path == sample_event_file_data.splits_path
    assert created_event_file.results_path == sample_event_file_data.results_path

    # Try to create the same event file again (should raise HTTPException)
    # with pytest.raises(HTTPException):
    #     await service.create(sample_event_file_data)

    # Clean up by deleting the created event file (if necessary)
    await service.delete(created_event_file.id)


async def test_get_all_event_files(session: AsyncSession):
    service = EventFileService(session)

    # Retrieve all event files (expecting at least one)
    all_event_files = await service.get_all()
    assert len(all_event_files) > 0

    # Clean up by deleting all event files (if necessary)
    for event_file in all_event_files:
        await service.delete(event_file.id)


async def test_get_event_file_by_id(session: AsyncSession, sample_event_file_data: EventFileInput):
    service = EventFileService(session)

    # Create a new event file
    created_event_file = await service.create(sample_event_file_data)

    # Retrieve the event file by ID
    retrieved_event_file = await service.get_event_file(created_event_file.id)

    # Verify the retrieved event file matches the created event file
    assert retrieved_event_file.splits_path == sample_event_file_data.splits_path
    assert retrieved_event_file.results_path == sample_event_file_data.results_path

    # Try to retrieve a non-existent event file (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.get_event_file(uuid4())

    # Clean up by deleting the created event file
    await service.delete(created_event_file.id)


async def test_update_event_file(session: AsyncSession, sample_event_file_data: EventFileInput, updated_event_file_data: EventFileInput):
    service = EventFileService(session)

    # Create a new event file
    created_event_file = await service.create(sample_event_file_data)

    # Update the event file's information
    updated_event_file = await service.update(created_event_file.id, updated_event_file_data)

    # Verify the updated event file has the new attributes
    assert updated_event_file.splits_path == updated_event_file_data.splits_path
    assert updated_event_file.results_path == updated_event_file_data.results_path

    # Try to update a non-existent event file (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.update(uuid4(), updated_event_file_data)

    # Clean up by deleting the created event file
    await service.delete(created_event_file.id)


async def test_delete_event_file(session: AsyncSession, sample_event_file_data: EventFileInput):
    service = EventFileService(session)

    # Create a new event file
    created_event_file = await service.create(sample_event_file_data)

    # Delete the event file and verify
    result = await service.delete(created_event_file.id)
    assert result is True

    # Try to delete a non-existent event file (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.delete(uuid4())

    # Clean up by deleting the created event file (if necessary)
    # Note: Depending on your implementation, the event file might already be deleted in the previous step.

