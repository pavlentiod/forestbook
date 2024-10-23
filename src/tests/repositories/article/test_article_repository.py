import pytest

from src.database.models.user.user import User
from src.repositories.article.article_repository import ArticleRepository
from src.schemas.article.article_schema import ArticleInput


@pytest.mark.asyncio
class TestArticleRepository:

    @pytest.fixture
    async def create_user(self, session):
        """Fixture to create a user for authoring articles."""
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            hashed_password=b"hashedpassword",
            access=1,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @pytest.fixture
    async def article_repo(self, session):
        """Fixture to initialize the ArticleRepository."""
        return ArticleRepository(session)

    @pytest.mark.asyncio
    async def test_create_article(self, article_repo, create_user):
        """Test for creating an article in the repository."""
        data = ArticleInput(
            title="Sample Article",
            content="This is a test article.",
            author_id=create_user.id
        )
        article = await article_repo.create(data)

        assert article.title == "Sample Article"
        assert article.content == "This is a test article."
        assert article.author_id == create_user.id
        assert article.created_at is not None

    @pytest.mark.asyncio
    async def test_get_all_articles(self, article_repo, create_user):
        """Test for retrieving all articles."""
        data_1 = ArticleInput(
            title="First Article",
            content="Content of the first article.",
            author_id=create_user.id
        )
        data_2 = ArticleInput(
            title="Second Article",
            content="Content of the second article.",
            author_id=create_user.id
        )
        await article_repo.create(data_1)
        await article_repo.create(data_2)

        articles = await article_repo.get_all()

        assert len(articles) == 2
        assert articles[0].title == "First Article"
        assert articles[1].title == "Second Article"

    @pytest.mark.asyncio
    async def test_get_article_by_id(self, article_repo, create_user):
        """Test for retrieving a specific article by its ID."""
        data = ArticleInput(
            title="Unique Article",
            content="Content of the unique article.",
            author_id=create_user.id
        )
        article = await article_repo.create(data)

        fetched_article = await article_repo.get_by_id(article.id)

        assert fetched_article.id == article.id
        assert fetched_article.title == "Unique Article"

    @pytest.mark.asyncio
    async def test_update_article(self, article_repo, create_user):
        """Test for updating an article."""
        data = ArticleInput(
            title="Old Title",
            content="Old content.",
            author_id=create_user.id
        )
        article = await article_repo.create(data)

        update_data = ArticleInput(
            title="Updated Title",
            content="Updated content.",
            author_id=create_user.id
        )
        updated_article = await article_repo.update(article, update_data)

        assert updated_article.title == "Updated Title"
        assert updated_article.content == "Updated content."

    @pytest.mark.asyncio
    async def test_delete_article(self, article_repo, create_user):
        """Test for deleting an article."""
        data = ArticleInput(
            title="Article to be deleted",
            content="This article will be deleted.",
            author_id=create_user.id
        )
        article = await article_repo.create(data)

        assert await article_repo.get_by_id(article.id) is not None

        await article_repo.delete(article)

        assert await article_repo.get_by_id(article.id) is None
