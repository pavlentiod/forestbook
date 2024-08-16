import asyncio
from typing import List, Optional, Type

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models.event.event import Event
from schemas.event.event_schema import EventInput, EventOutput


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: EventInput) -> EventOutput:
        event = Event(
            title=data.title,
            count=data.count,
            split_link=data.split_link,
            date=data.date,
            status=data.status
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return EventOutput(
            id=event.id,
            title=event.title,
            count=event.count,
            split_link=event.split_link,
            date=event.date,
            status=event.status,
        )

    async def get_all(self) -> List[Optional[EventOutput]]:
        stmt = select(Event).order_by(Event.id)
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        return [EventOutput(**event.__dict__) for event in events]

    async def get_event(self, _id: UUID4) -> EventOutput:
        event = await self.session.get(Event, _id)
        return EventOutput(**event.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[Event]:
        return await self.session.get(Event, _id)

    async def get_by_source_link(self, link: str) -> Optional[EventOutput]:
        if "#" in link:
            link = link[:link.index("#")]
        event = await self.session.scalar(select(Event).where(Event.split_link == link))
        if event:
            return EventOutput(**event.__dict__)

    async def event_exists_by_id(self, _id: UUID4) -> bool:
        event = await self.session.get(Event, _id)
        return event is not None

    async def update(self, event: Type[Event], data: EventInput) -> EventOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(event, key, value)
        await self.session.commit()
        await self.session.refresh(event)
        return EventOutput(**event.__dict__)

    async def delete(self, event: Type[Event]) -> bool:
        await self.session.delete(event)
        await self.session.commit()
        return True



