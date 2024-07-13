from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repository.event.event_repository import EventRepository
from schemas.event.event_schema import EventInput

@pytest.fixture
def sample_event_data() -> EventInput:
    return EventInput(
        title="Sample Event",
        count=10,
        split_link="http://example.com",
        date=datetime(2024, 7, 12),
        status=True
    )

@pytest.fixture
def updated_event_data() -> EventInput:
    return EventInput(
        title="Updated Event",
        count=20,
        split_link="http://example.com/updated",
        date=datetime(2024, 8, 12),
        status=False
    )


async def test_create(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    event = await event_repository.create(sample_event_data)

    assert event.title == sample_event_data.title
    assert event.count == sample_event_data.count
    assert event.split_link == sample_event_data.split_link
    assert event.date == sample_event_data.date
    assert event.status == sample_event_data.status

async def test_get_all(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    await event_repository.create(sample_event_data)
    events = await event_repository.get_all()

    assert len(events) > 0
    assert events[0].title == sample_event_data.title

async def test_get_event(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    created_event = await event_repository.create(sample_event_data)
    event = await event_repository.get_event(created_event.id)

    assert event.title == sample_event_data.title
    assert event.id == created_event.id

async def test_get_by_id(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    created_event = await event_repository.create(sample_event_data)
    event = await event_repository.get_by_id(created_event.id)

    assert event is not None
    assert event.id == created_event.id

async def test_event_exists_by_id(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    created_event = await event_repository.create(sample_event_data)
    exists = await event_repository.event_exists_by_id(created_event.id)

    assert exists is True

async def test_update(session: AsyncSession, sample_event_data: EventInput, updated_event_data: EventInput):
    event_repository = EventRepository(session=session)
    created_event = await event_repository.create(sample_event_data)
    event = await event_repository.get_by_id(created_event.id)
    updated_event = await event_repository.update(event, updated_event_data)

    assert updated_event.title == updated_event_data.title
    assert updated_event.count == updated_event_data.count

async def test_delete(session: AsyncSession, sample_event_data: EventInput):
    event_repository = EventRepository(session=session)
    created_event = await event_repository.create(sample_event_data)
    event = await event_repository.get_by_id(created_event.id)
    success = await event_repository.delete(event)

    assert success is True
    exists = await event_repository.event_exists_by_id(created_event.id)
    assert exists is False

