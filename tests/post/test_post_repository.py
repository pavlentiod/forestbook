from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.post.post_repository import PostRepository
from schemas.post.post_schema import PostInput

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
    post_repository = PostRepository(session=session)
    post = await post_repository.create(sample_post_data)

    assert post.title == sample_post_data.title
    assert post.place == sample_post_data.place
    assert post.median_p_bk == sample_post_data.median_p_bk
    assert post.result == sample_post_data.result
    assert post.backlog == sample_post_data.backlog
    assert post.points_number == sample_post_data.points_number
    assert post.split_firsts == sample_post_data.split_firsts
    assert post.image_path == sample_post_data.image_path
    assert post.split == sample_post_data.split
    assert post.index == sample_post_data.index
    assert post.body == sample_post_data.body


async def test_get_all_posts(session: AsyncSession, sample_post_data: PostInput):
    post_repository = PostRepository(session=session)
    await post_repository.create(sample_post_data)
    posts = await post_repository.get_all()

    assert len(posts) > 0
    assert posts[0].title == sample_post_data.title


async def test_get_post_by_id(session: AsyncSession, sample_post_data: PostInput):
    post_repository = PostRepository(session=session)
    created_post = await post_repository.create(sample_post_data)
    post = await post_repository.get_post(created_post.id)

    assert post.title == sample_post_data.title
    assert post.id == created_post.id


async def test_get_by_id(session: AsyncSession, sample_post_data: PostInput):
    post_repository = PostRepository(session=session)
    created_post = await post_repository.create(sample_post_data)
    post = await post_repository.get_by_id(created_post.id)

    assert post is not None
    assert post.id == created_post.id


async def test_post_exists_by_id(session: AsyncSession, sample_post_data: PostInput):
    post_repository = PostRepository(session=session)
    created_post = await post_repository.create(sample_post_data)
    exists = await post_repository.post_exists_by_id(created_post.id)

    assert exists is True


async def test_update_post(session: AsyncSession, sample_post_data: PostInput, updated_post_data: PostInput):
    post_repository = PostRepository(session=session)
    created_post = await post_repository.create(sample_post_data)
    post = await post_repository.get_by_id(created_post.id)
    updated_post = await post_repository.update(post, updated_post_data)

    assert updated_post.title == updated_post_data.title
    assert updated_post.place == updated_post_data.place
    assert updated_post.median_p_bk == updated_post_data.median_p_bk
    assert updated_post.result == updated_post_data.result
    assert updated_post.backlog == updated_post_data.backlog
    assert updated_post.points_number == updated_post_data.points_number
    assert updated_post.split_firsts == updated_post_data.split_firsts
    assert updated_post.image_path == updated_post_data.image_path
    assert updated_post.split == updated_post_data.split
    assert updated_post.index == updated_post_data.index
    assert updated_post.body == updated_post_data.body


async def test_delete_post(session: AsyncSession, sample_post_data: PostInput):
    post_repository = PostRepository(session=session)
    created_post = await post_repository.create(sample_post_data)
    post = await post_repository.get_by_id(created_post.id)
    success = await post_repository.delete(post)

    assert success is True
    exists = await post_repository.post_exists_by_id(created_post.id)
    assert exists is False
