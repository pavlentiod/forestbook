from typing import List, Optional
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from repository.event.event_repository import EventRepository
from schemas.event.event_schema import EventInput, EventOutput


class EventService:
    """
    Service class for handling events.
    """

    def __init__(self, session: AsyncSession):
        self.repository = EventRepository(session)

    async def create(self, data: EventInput) -> EventOutput:
        # Business logic validation can be added here if necessary
        return await self.repository.create(data)


    async def get_all(self) -> List[EventOutput]:
        return await self.repository.get_all()

    async def get_event(self, _id: UUID4) -> EventOutput:
        event = await self.repository.get_by_id(_id)
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
