import asyncio
from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db_helper
from src.database.models.post.post import Post
from src.schemas.post.post_schema import PostInput, PostOutput


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: PostInput) -> PostOutput:
        post = Post(
            title=data.title,
            body=data.body,
            user_id=data.user_id,
            event_id=data.event_id,
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(
            id=post.id,
            title=post.title,
            body=post.body,
            created_date=post.created_date,
            user_id=post.user_id,
            event_id=post.event_id,
        )

    async def get_all(self) -> List[Optional[PostOutput]]:
        stmt = select(Post).order_by(Post.created_date)
        result = await self.session.execute(stmt)
        posts = result.scalars().all()
        return [PostOutput(**post.__dict__) for post in posts]

    async def get_post(self, _id: UUID4) -> PostOutput:
        post = await self.session.get(Post, _id)
        return PostOutput(**post.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[Post]:
        return await self.session.get(Post, _id)

    async def post_exists_by_id(self, _id: UUID4) -> bool:
        post = await self.session.get(Post, _id)
        return post is not None

    async def update(self, post: Post, data: PostInput) -> PostOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(post, key, value)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(**post.__dict__)

    async def delete(self, post: Post) -> bool:
        await self.session.delete(post)
        await self.session.commit()
        return True
