import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from schemas.post.post_schema import PostInput
from service.post.post_service import PostService


@pytest.fixture
def sample_post_data() -> PostInput:
    return PostInput(
        title="Sample Post",
        place=1,
        median_p_bk=100,
        result=50,
        backlog=10,
        points_number=30,
        split_firsts=5,
        image_path="images/sample.jpg",
        split={"key": "value"},
        index="index_sample",
        body={"content": "This is a sample post body"},
        user_id="2494f7df-d104-4848-a19e-7cae30960ced",
        event_id="e894c953-d404-4311-aea8-bc7098393157"
    )

@pytest.fixture
def updated_post_data() -> PostInput:
    return PostInput(
        title="Updated Post",
        place=2,
        median_p_bk=150,
        result=60,
        backlog=5,
        points_number=35,
        split_firsts=7,
        image_path="images/updated.jpg",
        split={"key": "new_value"},
        index="index_updated",
        body={"content": "This is an updated post body"},
        user_id="2494f7df-d104-4848-a19e-7cae30960ced",
        event_id="e894c953-d404-4311-aea8-bc7098393157"
    )



async def test_create_post(session: AsyncSession, sample_post_data: PostInput):
    service = PostService(session)

    # Create a new post
    created_post = await service.create(sample_post_data)

    # Verify the created post has the expected attributes
    assert created_post.title == sample_post_data.title
    assert created_post.body == sample_post_data.body

    # Try to create the same post again (should raise HTTPException)
    # with pytest.raises(HTTPException):
    #     await service.create(sample_post_data)

    # Clean up by deleting the created post (if necessary)
    await service.delete(created_post.id)


async def test_get_all_posts(session: AsyncSession):
    service = PostService(session)

    # Retrieve all posts (expecting at least one)
    all_posts = await service.get_all()
    assert len(all_posts) > 0

    # Clean up by deleting all posts (if necessary)
    for post in all_posts:
        await service.delete(post.id)


async def test_get_post_by_id(session: AsyncSession, sample_post_data: PostInput):
    service = PostService(session)

    # Create a new post
    created_post = await service.create(sample_post_data)

    # Retrieve the post by ID
    retrieved_post = await service.get_post(created_post.id)

    # Verify the retrieved post matches the created post
    assert retrieved_post.title == sample_post_data.title
    assert retrieved_post.body == sample_post_data.body

    # Try to retrieve a non-existent post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.get_post(uuid4())

    # Clean up by deleting the created post
    await service.delete(created_post.id)


async def test_update_post(session: AsyncSession, sample_post_data: PostInput, updated_post_data: PostInput):
    service = PostService(session)

    # Create a new post
    created_post = await service.create(sample_post_data)

    # Update the post's information
    updated_post = await service.update(created_post.id, updated_post_data)

    # Verify the updated post has the new attributes
    assert updated_post.title == updated_post_data.title
    assert updated_post.body == updated_post_data.body

    # Try to update a non-existent post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.update(uuid4(), updated_post_data)

    # Clean up by deleting the created post
    await service.delete(created_post.id)


async def test_delete_post(session: AsyncSession, sample_post_data: PostInput):
    service = PostService(session)

    # Create a new post
    created_post = await service.create(sample_post_data)

    # Delete the post and verify
    result = await service.delete(created_post.id)
    assert result is True

    # Try to delete a non-existent post (should raise HTTPException)
    with pytest.raises(HTTPException):
        await service.delete(uuid4())

    # Clean up by deleting the created post (if necessary)
    # Note: Depending on your implementation, the post might already be deleted in the previous step.

