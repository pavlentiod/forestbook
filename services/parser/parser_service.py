import asyncio
import datetime
import json
import uuid
from io import BytesIO

from fastapi import UploadFile

from schemas.event.event_schema import EventInput
from schemas.results.results_schema import Results
from services.parser.parser_utils import web_parse, file_parse, parse_event, calculate_results



class ParserService:

    def parse(self, source_link: str = "", source_file: UploadFile = None):  # returns EventInput + Results
        page = self.get_source(source_link,source_file)
        try:
            event_df, routes = parse_event(page)
            results = calculate_results(event_df.copy())
        except Exception as e:
            print(e)
            return None
        event = EventInput(
            count=event_df.shape[0],
            status=True,
            split_link = source_link,
            date=datetime.datetime.now()
        )
        results = Results(
            splits=event_df.to_dict(orient='split'),
            routes=routes,
            results=results
        )
        return event, results

    def get_source(self, source_link, source_file):
        if source_link:
            return web_parse(source_link)
        else:
            return file_parse(source_file)


# async def main():
#     async with db_helper.session_factory() as session:
#         parser = ParserService()
#         ev, res = parser.parse(source_link="https://o-saratov.ru/api/media/uploads/%D0%A1%D0%BF%D0%BB%D0%B8%D1%82%D1%8B_2_%D0%B4%D0%B5%D0%BD%D1%8C_%D0%9C_21.htm")
#         ev_service = EventService(session=session)
#         ev.title = "Narat"
#         event = await ev_service.create(ev)


# storage = StorageService()
# data = asyncio.run(storage.download_json("routes.json"))
# # # file = asyncio.run(storage.upload("Events/Splits/00285ec9-fe2e-49e2-b800-2ebbfc57bd6b.csv"))
# # # print(data)
# # file = UploadFile(file=BytesIO(json.dumps(res.splits).encode('UTF-8')), filename="jsonsplits.json")
# # file2 = asyncio.run(storage.upload_to_json(data=res.routes, filename="routes.json"))
# print(data)
# if __name__ == "__main__":
#      asyncio.run(main())