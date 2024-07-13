import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repository.event.event_file_repository import EventFileRepository
from schemas.event.event_file_schema import EventFileInput


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


async def test_create(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    event_file = await event_file_repository.create(sample_event_file_data)

    assert event_file.splits_path == sample_event_file_data.splits_path
    assert event_file.routes_path == sample_event_file_data.routes_path
    assert event_file.results_path == sample_event_file_data.results_path
    assert event_file.event_id == sample_event_file_data.event_id
#
async def test_get_all(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    await event_file_repository.create(sample_event_file_data)
    event_files = await event_file_repository.get_all()

    assert len(event_files) > 0
    assert event_files[0].splits_path == sample_event_file_data.splits_path

async def test_get_event_file(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    created_event_file = await event_file_repository.create(sample_event_file_data)
    event_file = await event_file_repository.get_event_file(created_event_file.id)

    assert event_file.splits_path == sample_event_file_data.splits_path
    assert event_file.id == created_event_file.id

async def test_get_by_id(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    created_event_file = await event_file_repository.create(sample_event_file_data)
    event_file = await event_file_repository.get_by_id(created_event_file.id)

    assert event_file is not None
    assert event_file.id == created_event_file.id

async def test_event_file_exists_by_id(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    created_event_file = await event_file_repository.create(sample_event_file_data)
    exists = await event_file_repository.event_file_exists_by_id(created_event_file.id)

    assert exists is True

async def test_update(session: AsyncSession, sample_event_file_data: EventFileInput, updated_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    created_event_file = await event_file_repository.create(sample_event_file_data)
    event_file = await event_file_repository.get_by_id(created_event_file.id)
    updated_event_file = await event_file_repository.update(event_file, updated_event_file_data)

    assert updated_event_file.splits_path == updated_event_file_data.splits_path
    assert updated_event_file.routes_path == updated_event_file_data.routes_path

async def test_delete(session: AsyncSession, sample_event_file_data: EventFileInput):
    event_file_repository = EventFileRepository(session=session)
    created_event_file = await event_file_repository.create(sample_event_file_data)
    event_file = await event_file_repository.get_by_id(created_event_file.id)
    success = await event_file_repository.delete(event_file)

    assert success is True
    exists = await event_file_repository.event_file_exists_by_id(created_event_file.id)
    assert exists is False

