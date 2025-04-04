import asyncio
from typing import Optional, List
from uuid import UUID
import httpx
import logging

from forestlab_schemas.event import EventEndpoint, EventUpdate, EventResponse
from forestlab_schemas.track import TrackResponse
from forestlab_schemas.runner import RunnerStat, RunnerOutput
from forestlab_schemas.course import CourseOutput
from forestlab_schemas.group import GroupOutput
from forestlab_schemas.leg import LegOutput
from forestlab_schemas.leaderboard import LeaderBoard

from src.config import settings

logger = logging.getLogger(__name__)


class ForestLabClient:
    """
    Асинхронный клиент для взаимодействия с ForestLab API.
    """

    def __init__(self):
        self.base_url = "http://127.0.0.1:8020"
        # self.base_url = settings.services.forestlab.base_url
        self.timeout = 5
        self.headers = {
            "X-Internal-Token": ""  # при необходимости убрать или заменить
        }
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _get(self, path: str) -> dict:
        try:
            response = await self.client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GET {path} failed: {e.response.status_code} {e.response.text}")
            print(f"Ошибка {e.response.status_code}: {e.response.text}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error during GET {path}")
            raise

    async def _post(self, path: str, data: dict) -> dict:
        try:
            response = await self.client.post(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"POST {path} failed: {e.response.status_code} {e.response.text}")
            raise

    async def _put(self, path: str, data: dict) -> dict:
        response = await self.client.put(path, json=data)
        response.raise_for_status()
        return response.json()

    async def _delete(self, path: str) -> None:
        response = await self.client.delete(path)
        response.raise_for_status()

    # ---------- PUBLIC METHODS ----------

    async def get_events(self) -> List[EventResponse]:
        data = await self._get("/events/")
        return [EventResponse(**event) for event in data]

    async def get_event(self, event_id: UUID) -> EventResponse:
        data = await self._get(f"/events/{event_id}")
        return EventResponse(**data)

    async def create_event(self, event: EventEndpoint) -> EventResponse:
        data = await self._post("/events/", event.model_dump())
        return EventResponse(**data)

    async def update_event(self, event_id: UUID, update: EventUpdate) -> EventResponse:
        data = await self._put(f"/events/{event_id}", update.model_dump())
        return EventResponse(**data)

    async def delete_event(self, event_id: UUID) -> bool:
        await self._delete(f"/events/{event_id}")
        return True

    async def get_runner_stat(self, event_id: UUID, runner_id: UUID) -> RunnerStat:
        data = await self._get(f"/events/{event_id}/statistics/runners/{runner_id}")
        return RunnerStat(**data)

    async def get_runner_output(self, event_id: UUID, runner_id: UUID) -> RunnerOutput:
        data = await self._get(f"/events/{event_id}/runners/{runner_id}")
        return RunnerOutput(**data)

    async def get_courses(self, event_id: UUID) -> List[CourseOutput]:
        data = await self._get(f"/events/{event_id}/courses")
        return [CourseOutput(**course) for course in data]

    async def get_groups(self, event_id: UUID) -> List[GroupOutput]:
        data = await self._get(f"/events/{event_id}/groups")
        return [GroupOutput(**group) for group in data]

    async def get_legs(self, event_id: UUID) -> List[LegOutput]:
        data = await self._get(f"/events/{event_id}/legs")
        return [LegOutput(**leg) for leg in data]

    async def get_track(self, event_id: UUID, runner_id: UUID, track_id: UUID) -> TrackResponse:
        data = await self._get(f"/events/{event_id}/runners/{runner_id}/track?track_id={track_id}")
        return TrackResponse(**data)

    async def delete_track(self, event_id: UUID, runner_id: UUID, track_id: UUID) -> bool:
        await self._delete(f"/events/{event_id}/runners/{runner_id}/track?track_id={track_id}")
        return True

    async def upload_track(self, event_id: UUID, runner_id: UUID, file_path: str) -> TrackResponse:
        with open(file_path, "rb") as f:
            files = {"file": ("track.gpx", f, "application/gpx+xml")}
            response = await self.client.post(
                f"/events/{event_id}/runners/{runner_id}/track",
                files=files
            )
            response.raise_for_status()
            return TrackResponse(**response.json())

    async def get_leaderboard(self, course_id: UUID) -> LeaderBoard:
        data = await self._get(f"/leaderboard/course/{course_id}")
        return LeaderBoard(**data)


