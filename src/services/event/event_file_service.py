from typing import List
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.repositories.event.event_file_repository import EventFileRepository
from src.schemas.event.event_file_schema import EventFileInput, EventFileOutput


class EventFileService:
    """
    Service class for handling event files.
    """

    def __init__(self, session: AsyncSession):
        self.repository = EventFileRepository(session)

    async def create(self, event_id: UUID4) -> EventFileOutput:
        # TODO add event exist validation
        event_files_input = EventFileInput(event_id=event_id)
        return await self.repository.create(event_files_input)


    # async def upload_files_to_storage(self, event_files: Results) -> bool:


    async def get_all(self) -> List[EventFileOutput]:
        return await self.repository.get_all()

    async def get_event_file(self, _id: UUID4) -> EventFileOutput:
        event_file = await self.repository.get_by_id(_id)
        if not event_file:
            raise HTTPException(status_code=404, detail="Event file not found")
        return event_file

    async def get_event_file_by_event_id(self, _id: UUID4) -> EventFileOutput:
        event_file = await self.repository.get_by_event_id(_id)
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
