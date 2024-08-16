from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.event.event_repository import EventRepository
from src.schemas.event.event_schema import EventInput, EventOutput, EventEndpoint
from src.services.event.event_file_service import EventFileService
from src.services.parser.parser_service import ParserService
from src.services.storage.storage_service import StorageService


class EventService:
    """
    Service class for handling events.
    """

    def __init__(self, session: AsyncSession):
        self.repository = EventRepository(session)
        self.filesService = EventFileService(session)

    async def create(self, data_from_api: EventEndpoint) -> EventOutput:
        # TODO: add EventEndpoint data validation
        # Check if event exist
        exist = await self.repository.get_by_source_link(data_from_api.split_link)
        if exist:
            files = await self.filesService.get_event_file_by_event_id(exist.id)
            exist.event_files = files
            return exist

        # Parse data from link
        parserService = ParserService()
        event, results = parserService.parse(source_link=data_from_api.split_link)

        # Update EventInput object and add to db
        event.title = data_from_api.title
        event.date = data_from_api.date
        event_from_db = await self.repository.create(event)

        # Add event files to db and update event
        event_files_output = await self.filesService.create(event_id=event_from_db.id)
        event_from_db.event_files = event_files_output

        # Upload files with results to storage
        storageService = StorageService()
        await storageService.upload_results(results=results, filenames=event_files_output)

        return event_from_db

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

#
# async def main():
#     async with db_helper.session_factory() as session:
#         endpoint1 = EventEndpoint(
#             title="narat",
#             split_link="https://o-saratov.ru/api/media/uploads/%D0%A1%D0%BF%D0%BB%D0%B8%D1%82%D1%8B_2_%D0%B4%D0%B5%D0%BD%D1%8C_%D0%9C_21.htm",
#             date=datetime.datetime.strptime("2 June, 2003", "%d %B, %Y")
#         )
#         endpoint2 = EventEndpoint(
#             title="univers3",
#             split_link="https://o-bash.ru/wp-content/uploads/2024/07/18.07-Splity.html?s_splits=1&sportorg=1",
#             date=datetime.datetime.strptime("19 July, 2024", "%d %B, %Y")
#         )
#         service = EventService(session)
#         ev = await service.create(data_from_api=endpoint1)
#         print(ev)
        # results_service = ResultsService(event=ev)
        # user = UserOutput(
        #     first_name="Павел",
        #     last_name="Иванов",
        #     id=uuid.uuid4(),
        #     email='mail@mail.ti',
        #     access=1,
        #     is_active=True
        # )
        # spl = SplitInput(
        #     user=user,
        #     sort_by=""
        # )
        # post = await results_service.calculate_post(split=spl)
        # print(post)
        # post_service = PostService(session=session)
        # await post_service.create(post)




# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
