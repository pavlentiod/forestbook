# routers/event_file_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import UUID4

from database import db_helper
from services.event.event_file_service import EventFileService
from schemas.event.event_file_schema import EventFileInput, EventFileOutput

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED, response_model=EventFileOutput)
async def create_event_file(
        data: EventFileInput,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = EventFileService(session)
    return await _service.create(data)

@router.get("", status_code=status.HTTP_200_OK, response_model=List[EventFileOutput])
async def get_event_files(session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> List[EventFileOutput]:
    _service = EventFileService(session)
    return await _service.get_all()

@router.get("/{_id}", status_code=status.HTTP_200_OK, response_model=EventFileOutput)
async def get_event_file(
        _id: UUID4,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = EventFileService(session)
    return await _service.get_event_file(_id)

@router.put("/{_id}", status_code=status.HTTP_200_OK, response_model=EventFileOutput)
async def update_event_file(
        _id: UUID4,
        data: EventFileInput,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = EventFileService(session)
    return await _service.update(_id, data)

@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_file(
        _id: UUID4,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    _service = EventFileService(session)
    await _service.delete(_id)
    return {"detail": "Event file deleted successfully"}
