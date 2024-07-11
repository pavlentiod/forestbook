# conftest.py

import pytest

from database import db_helper
from repository.event.event_repository import EventRepository
from schemas.event.event_file_schema import EventFileOutput
from schemas.event.event_schema import EventInput
from schemas.post.post_schema import PostOutput


@pytest.fixture(scope="module")
def db_session():
    return db_helper.get_scoped_session()


@pytest.fixture
def event_repository(db_session):
    event = EventRepository(db_session)
    return event


@pytest.fixture
def sample_event_data():
    return EventInput(
        title="Sample Event",
        count=10,
        status=True,
        split_link="https://example.com",
        date="2024-07-12T12:00:00"
    )


