from src.schemas.event.event_schema import EventOutput
from src.schemas.post.gps_post_schema import GPSPostInput
from src.schemas.post.post_schema import PostInput
from src.schemas.results.results_schema import Results
from src.schemas.split.split_schema import SplitInput
from src.schemas.user.user_schema import UserOutput
from src.services.results.src.split import SPL
from src.services.storage.storage_service import StorageService


class ResultsService:

    def __init__(self, event: EventOutput):
        self.event = event
        self.storage = StorageService()

    async def calculate_post(self, split: SplitInput) -> PostInput:  # returns PostInput
        results = await self.get_results()
        # print(results)
        return SPL(split_input=split, results_data=results)

    def calculate_gps_post(self, user: UserOutput) -> GPSPostInput:
        pass

    async def get_results(self) -> Results:
        return Results(
            splits=await self.storage.download_json(self.event.event_files.splits_path),
            routes=await self.storage.download_json(self.event.event_files.routes_path),
            results=await self.storage.download_json(self.event.event_files.results_path)
        )


