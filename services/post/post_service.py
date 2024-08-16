from typing import List, Optional
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from repositories.post.post_repository import PostRepository
from schemas.post.post_schema import PostInput, PostOutput


class PostService:
    """
    Service class for handling posts.
    """

    def __init__(self, session: AsyncSession):
        self.repository = PostRepository(session)

    async def create(self, data: PostInput) -> PostOutput:
        # Business logic validation can be added here if necessary
        return await self.repository.create(data)

    async def get_all(self) -> List[PostOutput]:
        return await self.repository.get_all()

    async def get_post(self, _id: UUID4) -> PostOutput:
        post = await self.repository.get_by_id(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    async def update(self, _id: UUID4, data: PostInput) -> PostOutput:
        post = await self.repository.get_by_id(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        updated_post = await self.repository.update(post, data)
        return updated_post

    async def delete(self, _id: UUID4) -> bool:
        post = await self.repository.get_by_id(_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return await self.repository.delete(post)
