from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.post.post import Post
from src.schemas.post.post_schema import PostInput, PostOutput, PostEndpoint


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

    async def create(self, data: PostInput) -> PostOutput:
        """
        Creates a new post and stores it in the database.

        :param data: The input data to create the post
        :return: The created post as PostOutput
        """
        post = Post(
            title=data.title,
            body=data.body,
            user_id=data.user_id,
            event_id=data.event_id,
            track_id=data.track_id
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(
            id=post.id,
            title=post.title,
            body=post.body,
            user_id=post.user_id,
            event_id=post.event_id,
            track_id=post.track_id,
            created_at=post.created_at
        )

    async def get_all(self) -> List[Optional[PostOutput]]:
        """
        Retrieves all posts from the database, ordered by creation date.

        :return: A list of PostOutput objects representing all posts
        """
        stmt = select(Post).order_by(Post.created_at)
        result = await self.session.execute(stmt)
        posts = result.scalars().all()
        return [PostOutput(**post.__dict__) for post in posts]

    async def get_post(self, _id: UUID) -> PostOutput:
        """
        Retrieves a specific post by its ID.

        :param _id: The ID of the post to retrieve
        :return: The post as PostOutput if found, otherwise None
        """
        post = await self.session.get(Post, _id)
        if post:
            return PostOutput(
                id=post.id,
                title=post.title,
                body=post.body,
                user_id=post.user_id,
                event_id=post.event_id,
                track_id=post.track_id,
                created_at=post.created_at
            )
        return None

    async def update(self, post: Post, data: PostEndpoint) -> PostOutput:
        """
        Updates an existing post with the given data.

        :param post: The post instance to update
        :param data: The new data for updating the post
        :return: The updated post as PostOutput
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(post, key, value)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(
            id=post.id,
            title=post.title,
            body=post.body,
            user_id=post.user_id,
            event_id=post.event_id,
            track_id=post.track_id,
            created_at=post.created_at
        )

    async def delete(self, post: Post) -> bool:
        """
        Deletes a post from the database.

        :param post: The post to delete
        :return: True if the post was successfully deleted, otherwise False
        """
        await self.session.delete(post)
        await self.session.commit()
        return True
