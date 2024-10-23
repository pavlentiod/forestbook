from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.post.post_repository import PostRepository
from src.schemas.post.post_schema import PostInput, PostUpdate


@pytest.mark.anyio
class TestPostRepository:
    @pytest.fixture
    async def post_repo(self, session: AsyncSession):
        return PostRepository(session)

    @pytest.fixture
    async def create_post(self, post_repo: PostRepository):
        post_data = PostInput(
            title="Test Post",
            body="This is a test post",
            user_id=uuid4(),
            event_id=uuid4()
        )
        return await post_repo.create(post_data)

    async def test_create_post(self, post_repo: PostRepository):
        """Test creating a post."""
        post_data = PostInput(
            title="New Test Post",
            body="This is a new test post",
            user_id=uuid4(),
            event_id=uuid4()
        )
        post = await post_repo.create(post_data)

        assert post.id is not None
        assert post.title == "New Test Post"
        assert post.body == "This is a new test post"
        assert post.user_id is not None
        assert post.event_id is not None

    async def test_get_all_posts(self, post_repo: PostRepository, create_post):
        """Test retrieving all posts."""
        post = await create_post
        posts = await post_repo.get_all()

        assert len(posts) > 0
        assert posts[0].title == post.title

    async def test_get_post_by_id(self, post_repo: PostRepository, create_post):
        """Test retrieving a post by its ID."""
        post = await create_post
        retrieved_post = await post_repo.get_post(post.id)

        assert retrieved_post.id == post.id
        assert retrieved_post.title == post.title

    async def test_get_user_posts(self, post_repo: PostRepository, create_post):
        """Test retrieving all posts by a user."""
        post = await create_post
        user_posts = await post_repo.get_user_posts(post.user_id)

        assert len(user_posts) > 0
        assert user_posts[0].user_id == post.user_id
        assert user_posts[0].title == post.title

    async def test_update_post(self, post_repo: PostRepository, create_post):
        """Test updating a post."""
        post = await create_post
        updated_data = PostUpdate(title="Updated Post Title", body="Updated body text")
        updated_post = await post_repo.update(post, updated_data)

        assert updated_post.title == "Updated Post Title"
        assert updated_post.body == "Updated body text"

    async def test_delete_post(self, post_repo: PostRepository, create_post):
        """Test deleting a post."""
        post = await create_post
        deleted = await post_repo.delete(post)

        assert deleted is True
        assert await post_repo.get_post(post.id) is None
