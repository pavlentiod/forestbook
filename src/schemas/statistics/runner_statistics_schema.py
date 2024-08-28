from typing import List, Optional
from pydantic import BaseModel


class RunnerStatistic(BaseModel):
    """
    Class for return runner(on event)-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: Optional[str] = None
    result: Optional[int] = None
    group: Optional[str] = None
    place: Optional[int] = None
    course: List[str] = None
    splits: Optional[dict] = None
    gen_times: Optional[dict] = None
    backlogs: Optional[dict] = None
    p_backlogs: Optional[dict] = None
    s_places: Optional[dict] = None


class RunnerStatisticsRequest(BaseModel):
    """
    Class for receive runner(on event)-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: Optional[bool] = None
    result: Optional[bool] = None
    group: Optional[bool] = None
    place: Optional[bool] = None
    course: List[bool] = None
    splits: Optional[bool] = None
    gen_times: Optional[bool] = None
    backlogs: Optional[bool] = None
    p_backlogs: Optional[bool] = None
    s_places: Optional[bool] = None
