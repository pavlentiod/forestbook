from typing import List
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.repositories.post.gps_post_repository import GPSPostRepository
from src.schemas.post.gps_post_schema import GPSPostInput, GPSPostOutput


class GPSPostService:
    """
    Service class for handling GPS posts.
    """

    def __init__(self, session: AsyncSession):
        self.repository = GPSPostRepository(session)

    async def create(self, data: GPSPostInput) -> GPSPostOutput:
        # Business logic validation can be added here if necessary
        return await self.repository.create(data)

    async def get_all(self) -> List[GPSPostOutput]:
        return await self.repository.get_all()

    async def get_gps_post(self, _id: UUID4) -> GPSPostOutput:
        gps_post = await self.repository.get_by_id(_id)
        if not gps_post:
            raise HTTPException(status_code=404, detail="GPS Post not found")
        return gps_post

    async def update(self, _id: UUID4, data: GPSPostInput) -> GPSPostOutput:
        gps_post = await self.repository.get_by_id(_id)
        if not gps_post:
            raise HTTPException(status_code=404, detail="GPS Post not found")
        updated_gps_post = await self.repository.update(gps_post, data)
        return updated_gps_post

    async def delete(self, _id: UUID4) -> bool:
        gps_post = await self.repository.get_by_id(_id)
        if not gps_post:
            raise HTTPException(status_code=404, detail="GPS Post not found")
        return await self.repository.delete(gps_post)
