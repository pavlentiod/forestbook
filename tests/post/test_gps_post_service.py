import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from schemas.post.gps_post_schema import GPSPostInput
from service.post.gps_post_service import GPSPostService


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


async def test_create_gps_post(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    service = GPSPostService(session)

    # Create a new GPS post
    created_gps_post = await service.create(sample_gps_post_data)

    # Verify the created GPS post has the expected attributes
    assert created_gps_post.pace == sample_gps_post_data.pace
    assert created_gps_post.coord_data == sample_gps_post_data.coord_data

    # Try to create the same GPS post again (should raise HTTPException)
    # with pytest.raises(HTTPException):
    #     await service.create(sample_gps_post_data)

    # Clean up by deleting the created GPS post (if necessary)
    await service.delete(created_gps_post.id)


async def test_get_all_gps_posts(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    service = GPSPostService(session)
    created_gps_post = await service.create(sample_gps_post_data)
    # Retrieve all GPS posts (expecting at least one)
    all_gps_posts = await service.get_all()
    assert len(all_gps_posts) > 0

    # Clean up by deleting all GPS posts (if necessary)
    for gps_post in all_gps_posts:
        await service.delete(gps_post.id)


async def test_get_gps_post_by_id(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    service = GPSPostService(session)

    # Create a new GPS post
    created_gps_post = await service.create(sample_gps_post_data)

    # Retrieve the GPS post by ID
    retrieved_gps_post = await service.get_gps_post(created_gps_post.id)

    # Verify the retrieved GPS post matches the created GPS post
    assert retrieved_gps_post.climb == sample_gps_post_data.climb

    # Try to retrieve a non-existent GPS post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.get_gps_post(uuid4())

    # Clean up by deleting the created GPS post
    await service.delete(created_gps_post.id)


async def test_update_gps_post(session: AsyncSession, sample_gps_post_data: GPSPostInput, updated_gps_post_data: GPSPostInput):
    service = GPSPostService(session)

    # Create a new GPS post
    created_gps_post = await service.create(sample_gps_post_data)

    # Update the GPS post's information
    updated_gps_post = await service.update(created_gps_post.id, updated_gps_post_data)

    # Verify the updated GPS post has the new attributes
    assert updated_gps_post.climb == updated_gps_post_data.climb
    assert updated_gps_post.pace == updated_gps_post_data.pace

    # Try to update a non-existent GPS post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.update(uuid4(), updated_gps_post_data)

    # Clean up by deleting the created GPS post
    await service.delete(created_gps_post.id)


async def test_delete_gps_post(session: AsyncSession, sample_gps_post_data: GPSPostInput):
    service = GPSPostService(session)

    # Create a new GPS post
    created_gps_post = await service.create(sample_gps_post_data)

    # Delete the GPS post and verify
    result = await service.delete(created_gps_post.id)
    assert result is True

    # Try to delete a non-existent GPS post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.delete(uuid4())

    # Clean up by deleting the created GPS post (if necessary)
    # Note: Depending on your implementation, the GPS post might already be deleted in the previous step.

