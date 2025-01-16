from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.post.post import Post
from src.schemas.post.post_schema import PostInput, PostInDB, PostEndpoint, PostFilter, PostUpdate


class PostRepository:
    """
    Repository for handling operations related to the Post model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession to interact with the database
        """
        self.session = session

    async def create(self, data: PostInput) -> PostInDB:
        """
        Creates a new post and stores it in the database.

        :param data: The input data to create the post
        :return: The created post as PostInDB
        """
        post = Post(**data.model_dump())
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return PostInDB(**post.__dict__)

    async def get_all(self, filters: PostFilter) -> List[Optional[PostInDB]]:
        """
        Retrieves all posts from the database, applying optional filters.

        :param filters: PostFilter schema containing filtering criteria.
        :return: A list of PostInDB objects representing filtered posts.
        """
        query = select(Post)

        # Build filter conditions dynamically
        conditions = []
        if filters.user_id:
            conditions.append(Post.user_id == filters.user_id)
        if filters.event_id:
            conditions.append(Post.event_id == filters.event_id)
        if filters.track_id:
            conditions.append(Post.track_id == filters.track_id)
        if filters.status:
            conditions.append(Post.status == filters.status)
        if filters.tags:
            conditions.append(Post.tags.overlap(filters.tags))  # Assuming tags is a PostgreSQL array
        if filters.created_at_from:
            conditions.append(Post.created_at >= filters.created_at_from)
        if filters.created_at_to:
            conditions.append(Post.created_at <= filters.created_at_to)
        if filters.updated_at_from:
            conditions.append(Post.updated_at >= filters.updated_at_from)
        if filters.updated_at_to:
            conditions.append(Post.updated_at <= filters.updated_at_to)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Post.created_at)

        result = await self.session.execute(query)
        posts = result.scalars().all()
        return [PostInDB(**post.__dict__) for post in posts]

    async def get_post(self, _id: UUID) -> PostInDB:
        """
        Retrieves a specific post by its ID.

        :param _id: The ID of the post to retrieve
        :return: The post as PostInDB if found, otherwise None
        """
        post = await self.session.get(Post, _id)
        if post:
            return PostInDB(**post.__dict__)
        return None

    async def get_by_id(self, _id: UUID) -> Post:
        """
        Retrieves a specific post by its ID.

        :param _id: The ID of the post to retrieve
        :return: The post as PostInDB if found, otherwise None
        """
        post = await self.session.get(Post, _id)
        return post

    async def update(self, post: Post, data: PostUpdate) -> PostInDB:
        """
        Updates an existing post with the given data.

        :param post: The post instance to update
        :param data: The new data for updating the post
        :return: The updated post as PostInDB
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(post, key, value)
        await self.session.commit()
        await self.session.refresh(post)
        return PostInDB(**post.__dict__)

    async def delete(self, post: Post) -> bool:
        """
        Deletes a post from the database.

        :param post: The post to delete
        :return: True if the post was successfully deleted, otherwise False
        """
        await self.session.delete(post)
        await self.session.commit()
        return True
