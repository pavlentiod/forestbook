from typing import List, Optional
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import HTTPException

from repository.event.event_file_repository import EventFileRepository
from schemas.event.event_file_schema import EventFileInput, EventFileOutput


class EventFileService:
    """
    Service class for handling event files.
    """

    def __init__(self, session: AsyncSession):
        self.repository = EventFileRepository(session)

    async def create(self, data: EventFileInput) -> EventFileOutput:
        # Business logic validation can be added here if necessary
        return await self.repository.create(data)

    async def get_all(self) -> List[EventFileOutput]:
        return await self.repository.get_all()

    async def get_event_file(self, _id: UUID4) -> EventFileOutput:
        event_file = await self.repository.get_by_id(_id)
        if not event_file:
            raise HTTPException(status_code=404, detail="Event file not found")
        return event_file

    async def update(self, _id: UUID4, data: EventFileInput) -> EventFileOutput:
        event_file = await self.repository.get_by_id(_id)
        if not event_file:
            raise HTTPException(status_code=404, detail="Event file not found")
        updated_event_file = await self.repository.update(event_file, data)
        return updated_event_file

    async def delete(self, _id: UUID4) -> bool:
        event_file = await self.repository.get_by_id(_id)
        if not event_file:
            raise HTTPException(status_code=404, detail="Event file not found")
        return await self.repository.delete(event_file)
