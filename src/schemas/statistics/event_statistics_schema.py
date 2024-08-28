from typing import List, Optional

from pydantic import BaseModel


class EventStatistic(BaseModel):
    """
    Class for return event-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: Optional[str] = None
    groups: Optional[List[str]] = None


class EventStatisticRequest(BaseModel):
    """
    Class for receive event-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: Optional[bool] = None
    groups: Optional[bool] = None


