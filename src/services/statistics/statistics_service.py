from pandas import DataFrame

from src.schemas.event.event_schema import EventOutput
from src.services.statistics.src.stat_event import ResEvent
from src.services.statistics.src.stat_group import ResGroup
from src.services.statistics.src.stat_runner import ResRunner
from src.services.storage.storage_service import StorageService


class StatisticsService:
    """
    Service for calculate event, group and runner metrics on certain event(one day of event).
    """

    def __init__(self, event: EventOutput, group: str = None, runner: str = None):
        self.splits: DataFrame = self._get_splits(event)
        self.routes: dict = self._get_routes(event)
        self.event: ResEvent = ResEvent(legs_df=self.splits, dispersions=self.routes)
        if group:
            self.group: ResGroup = self._get_group_by_name(group)
        if runner:
            self.group: ResGroup = self._get_group_by_runner(runner)
            self.runner: ResRunner = self._get_runner_by_name(runner)
        if group and runner:
            self.group: ResGroup = self._get_group_by_name(group)
            self.runner = self._get_runner_by_name_and_group(name=runner, group=group)

    async def _get_splits(self, event) -> DataFrame:
        """
        Get runners splits on event legs like dataframe
        :return: Ordinary event dataframe with timedelta data
        """
        storage = StorageService()
        splits = await storage.download_json(event.event_files.splits_path)
        return DataFrame(splits, dtype="timedelta64[ns]")

    async def _get_routes(self, event) -> dict:
        """
        Get routes from S3 for runners on event
        :return: dict with all dispersions
        """
        storage = StorageService()
        return await storage.download_json(event.event_files.routes_path)

    async def _get_results(self, event) -> dict:
        """
        Get results from S3 and return like a dict
        :return:
        """
        pass

    def _get_runner_by_name(self, name) -> ResRunner:
        pass

    def _get_group_by_runner(self, name) -> ResRunner:
        pass

    def _get_runner_by_name_and_group(self, name: str, group: str) -> ResRunner:
        pass

    def _get_group_by_name(self, group_name) -> ResGroup:
        pass

