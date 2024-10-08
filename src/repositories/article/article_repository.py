from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.article.article import Article
from src.schemas.article.article_schema import ArticleInput, ArticleOutput, ArticleEndpoint


class ArticleRepository:
    """
    Repository for handling operations related to the Article model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession to interact with the database
        """
        self.session = session

    async def create(self, data: ArticleInput) -> ArticleOutput:
        """
        Creates a new article and stores it in the database.

        :param data: The input data to create the article
        :return: The created article as ArticleOutput
        """
        article = Article(
            title=data.title,
            content=data.content,
            author_id=data.author_id
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return ArticleOutput(
            id=article.id,
            title=article.title,
            content=article.content,
            author_id=article.author_id,
            created_at=article.created_at
        )

    async def get_all(self) -> List[Optional[ArticleOutput]]:
        """
        Retrieves all articles from the database, ordered by creation date.

        :return: A list of ArticleOutput objects representing all articles
        """
        stmt = select(Article).order_by(Article.created_at)
        result = await self.session.execute(stmt)
        articles = result.scalars().all()
        return [ArticleOutput(**article.__dict__) for article in articles]

    async def get_article(self, _id: UUID) -> ArticleOutput:
        """
        Retrieves a specific article by its ID.

        :param _id: The ID of the article to retrieve
        :return: The article as ArticleOutput if found, otherwise None
        """
        article = await self.session.get(Article, _id)
        if article:
            return ArticleOutput(
                id=article.id,
                title=article.title,
                content=article.content,
                author_id=article.author_id,
                created_at=article.created_at
            )
        return None

    async def update(self, article: Article, data: ArticleEndpoint) -> ArticleOutput:
        """
        Updates an existing article with the given data.

        :param article: The article instance to update
        :param data: The new data for updating the article
        :return: The updated article as ArticleOutput
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(article, key, value)
        await self.session.commit()
        await self.session.refresh(article)
        return ArticleOutput(
            id=article.id,
            title=article.title,
            content=article.content,
            author_id=article.author_id,
            created_at=article.created_at
        )

    async def delete(self, article: Article) -> bool:
        """
        Deletes an article from the database.

        :param article: The article to delete
        :return: True if the article was successfully deleted, otherwise False
        """
        await self.session.delete(article)
        await self.session.commit()
        return True

    async def article_exists_by_id(self, _id: UUID) -> bool:
        """
        Checks if an article exists by its ID.

        :param _id: The ID of the article
        :return: True if the article exists, otherwise False
        """
        article = await self.session.get(Article, _id)
        return article is not None
