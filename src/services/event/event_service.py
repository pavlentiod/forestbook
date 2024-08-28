import datetime
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.event.event_repository import EventRepository
from src.schemas.event.event_schema import EventInput, EventOutput, EventEndpoint
from src.services.parser.parser_service import ParserService
from src.services.storage.storage_service import StorageService


class EventService:
    """
    Service class for handling events.
    """

    def __init__(self, session: AsyncSession):
        self.repository = EventRepository(session)

    async def create(self, data_from_api: EventEndpoint) -> EventOutput:
        # TODO: add EventEndpoint data validation
        # Check if event exist
        exist = await self.repository.get_by_source_link(data_from_api.split_link)
        if exist:
            return exist

        # Parse data from link
        parserService = ParserService()
        event, results = parserService.parse(source_link=data_from_api.split_link)

        # Update EventInput object and add to db
        event.title = data_from_api.title
        event.date = data_from_api.date
        event_from_db = await self.repository.create(event)

        # Upload files with results to storage
        storageService = StorageService()
        await storageService.upload_event_data(results=results, filename=event_from_db.id)

        return event_from_db

    async def get_all(self) -> List[EventOutput]:
        return await self.repository.get_all()

    async def get_event(self, _id: UUID4) -> EventOutput:
        event = await self.repository.get_event(_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    async def update(self, _id: UUID4, data: EventInput) -> EventOutput:
        event = await self.repository.get_by_id(_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        updated_event = await self.repository.update(event, data)
        return updated_event

    async def delete(self, _id: UUID4) -> bool:
        event = await self.repository.get_by_id(_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return await self.repository.delete(event)

