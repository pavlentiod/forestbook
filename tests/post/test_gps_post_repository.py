import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.post.gps_post_repository import GPSPostRepository
from schemas.post.gps_post_schema import GPSPostInput

@pytest.fixture
def sample_gps_post_data() -> GPSPostInput:
    return GPSPostInput(
        lenght_s=5000,
        lenght_p=3000,
        climb=150,
        pace=5,
        gpx_path="gpx/sample.gpx",
        coord_data={"latitude": 50.0, "longitude": 19.0},
        post_id="cddfa9b3-8f80-4950-90af-94f07e1897d4"
    )

@pytest.fixture
def updated_gps_post_data() -> GPSPostInput:
    return GPSPostInput(
        lenght_s=6000,
        lenght_p=4000,
        climb=200,
        pace=6,
        gpx_path="gpx/updated.gpx",
        coord_data={"latitude": 51.0, "longitude": 20.0},
        post_id="cddfa9b3-8f80-4950-90af-94f07e1897d4"
    )

async def test_create(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    gps_post = await gps_post_repository.create(sample_gps_post_data)

    assert gps_post.lenght_s == sample_gps_post_data.lenght_s
    assert gps_post.lenght_p == sample_gps_post_data.lenght_p
    assert gps_post.climb == sample_gps_post_data.climb
    assert gps_post.pace == sample_gps_post_data.pace
    assert gps_post.gpx_path == sample_gps_post_data.gpx_path
    assert gps_post.coord_data == sample_gps_post_data.coord_data


async def test_get_all(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    await gps_post_repository.create(sample_gps_post_data)
    gps_posts = await gps_post_repository.get_all()

    assert len(gps_posts) > 0
    assert gps_posts[0].lenght_s == sample_gps_post_data.lenght_s


async def test_get_gps_post(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    created_gps_post = await gps_post_repository.create(sample_gps_post_data)
    gps_post = await gps_post_repository.get_gps_post(created_gps_post.id)

    assert gps_post.lenght_s == sample_gps_post_data.lenght_s
    assert gps_post.id == created_gps_post.id


async def test_get_by_id(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    created_gps_post = await gps_post_repository.create(sample_gps_post_data)
    gps_post = await gps_post_repository.get_by_id(created_gps_post.id)

    assert gps_post is not None
    assert gps_post.id == created_gps_post.id


async def test_gps_post_exists_by_id(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    created_gps_post = await gps_post_repository.create(sample_gps_post_data)
    exists = await gps_post_repository.gps_post_exists_by_id(created_gps_post.id)

    assert exists is True


async def test_update(session: AsyncSession, sample_gps_post_data: GPSPostInput, updated_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    created_gps_post = await gps_post_repository.create(sample_gps_post_data)
    gps_post = await gps_post_repository.get_by_id(created_gps_post.id)
    updated_gps_post = await gps_post_repository.update(gps_post, updated_gps_post_data)

    assert updated_gps_post.lenght_s == updated_gps_post_data.lenght_s
    assert updated_gps_post.lenght_p == updated_gps_post_data.lenght_p

async def test_delete(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    gps_post_repository = GPSPostRepository(session=session)
    created_gps_post = await gps_post_repository.create(sample_gps_post_data)
    gps_post = await gps_post_repository.get_by_id(created_gps_post.id)
    success = await gps_post_repository.delete(gps_post)

    assert success is True
    exists = await gps_post_repository.gps_post_exists_by_id(created_gps_post.id)
    assert exists is False


