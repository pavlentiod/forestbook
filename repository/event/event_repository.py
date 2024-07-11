from sqlalchemy.orm import Session
from database.models.event.event import Event
from schemas.event.event_schema import EventInput, EventOutput
from typing import List, Optional
from pydantic import UUID4


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: EventInput) -> EventOutput:
        event = Event(
            title=data.title,
            count=data.count,
            split_link=data.split_link,
            date=data.date,
            status=data.status
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return EventOutput(
            id=event.id,
            title=event.title,
            count=event.count,
            split_link=event.split_link,
            date=event.date,
            status=event.status,
            event_files=[],
            posts=[]
        )

    def get_all(self) -> List[Optional[EventOutput]]:
        events = self.session.query(Event).all()
        return [EventOutput(**event.__dict__) for event in events]

    def get_event(self, event_id: UUID4) -> EventOutput:
        event = self.session.query(Event).filter_by(id=event_id).first()
        return EventOutput(**event.__dict__)

    def get_by_id(self, event_id: UUID4) -> Optional[Event]:
        return self.session.query(Event).filter_by(id=event_id).first()

    def event_exists_by_id(self, event_id: UUID4) -> bool:
        event = self.session.query(Event).filter_by(id=event_id).first()
        return event is not None

    def update(self, event: Event, data: EventInput) -> EventOutput:
        event.title = data.title
        event.count = data.count
        event.split_link = data.split_link
        event.date = data.date
        event.status = data.status
        self.session.commit()
        self.session.refresh(event)
        return EventOutput(**event.__dict__)

    def delete(self, event: Event) -> bool:
        self.session.delete(event)
        self.session.commit()
        return True
