from sqlalchemy.orm import Session
from database.models.event.event_file import Event_file
from schemas.event.event_file_schema import EventFileInput, EventFileOutput
from typing import List, Optional
from uuid import UUID


class EventFileRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: EventFileInput) -> EventFileOutput:
        event_file = Event_file(
            splits_path=data.splits_path,
            routes_path=data.routes_path,
            results_path=data.results_path
        )
        self.session.add(event_file)
        self.session.commit()
        self.session.refresh(event_file)
        return EventFileOutput(
            id=event_file.id,
            splits_path=event_file.splits_path,
            routes_path=event_file.routes_path,
            results_path=event_file.results_path,
            event=None  # Assuming event relationship is not populated here
        )

    def get_all(self) -> List[Optional[EventFileOutput]]:
        event_files = self.session.query(Event_file).all()
        return [EventFileOutput(**event_file.__dict__) for event_file in event_files]

    def get_event_file(self, event_file_id: UUID) -> EventFileOutput:
        event_file = self.session.query(Event_file).filter_by(id=event_file_id).first()
        return EventFileOutput(**event_file.__dict__)

    def get_by_id(self, event_file_id: UUID) -> Optional[Event_file]:
        return self.session.query(Event_file).filter_by(id=event_file_id).first()

    def event_file_exists_by_id(self, event_file_id: UUID) -> bool:
        event_file = self.session.query(Event_file).filter_by(id=event_file_id).first()
        return event_file is not None

    def update(self, event_file: Event_file, data: EventFileInput) -> EventFileOutput:
        event_file.splits_path = data.splits_path
        event_file.routes_path = data.routes_path
        event_file.results_path = data.results_path
        self.session.commit()
        self.session.refresh(event_file)
        return EventFileOutput(**event_file.__dict__)

    def delete(self, event_file: Event_file) -> bool:
        self.session.delete(event_file)
        self.session.commit()
        return True
