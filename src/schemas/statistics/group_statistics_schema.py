from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel





class GroupStatistic(BaseModel):
    """
    Class for return group(on event)-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: Optional[str] = None
    runners: Optional[List[str]] = None
    results: Optional[dict] = None
    courses: Optional[dict] = None
    split_leaders: Optional[dict] = None


class GroupStatisticRequest(BaseModel):
    """
    Class for receive group(on event)-related statistic metrics.

    ! NOT COMPLETE !
    """
    name: str
    event: UUID
    runners: Optional[bool] = None
    results: Optional[bool] = None
    courses: Optional[bool] = None
    split_leaders: Optional[bool] = None



# EXAMPLE
# request = GroupStatisticRequest(name="Group", runners=True)
# response = GroupStatistic(name=request.name)
#
#
# def get_runners():
#     return ["runner1", "runner2"]
#
# def get_courses():
#     return ["course1", "course2"]
#
#
# if request.name:
#     response.__setattr__("name", request.name)
# if request.runners:
#     response.__setattr__("runners", get_runners())
# if request.courses:
#     response.__setattr__("courses", get_courses())
#
#
# print(response.model_dump(mode='json', exclude_unset=True))

