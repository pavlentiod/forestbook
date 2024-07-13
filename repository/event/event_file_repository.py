import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import UUID4

from database import db_helper
from schemas.event.event_file_schema import EventFileInput, EventFileOutput
from database.models.event.event_file import Event_file

class EventFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: EventFileInput) -> EventFileOutput:
        event_file = Event_file(
            splits_path=data.splits_path,
            routes_path=data.routes_path,
            results_path=data.results_path,
            event_id=data.event_id
        )

        self.session.add(event_file)
        await self.session.commit()
        await self.session.refresh(event_file)
        return EventFileOutput(
            id=event_file.id,
            splits_path=event_file.splits_path,
            routes_path=event_file.routes_path,
            results_path=event_file.results_path,
            event_id=event_file.event_id
        )

    async def get_all(self) -> List[Optional[EventFileOutput]]:
        stmt = select(Event_file).order_by(Event_file.id)
        result = await self.session.execute(stmt)
        event_files = result.scalars().all()
        return [EventFileOutput(**event_file.__dict__) for event_file in event_files]

    async def get_event_file(self, _id: UUID4) -> EventFileOutput:
        event_file = await self.session.get(Event_file, _id)
        return EventFileOutput(**event_file.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[Event_file]:
        return await self.session.get(Event_file, _id)

    async def event_file_exists_by_id(self, _id: UUID4) -> bool:
        event_file = await self.session.get(Event_file, _id)
        return event_file is not None

    async def update(self, event_file: Event_file, data: EventFileInput) -> EventFileOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(event_file, key, value)
        await self.session.commit()
        await self.session.refresh(event_file)
        return EventFileOutput(**event_file.__dict__)

    async def delete(self, event_file: Event_file) -> bool:
        await self.session.delete(event_file)
        await self.session.commit()
        return True

