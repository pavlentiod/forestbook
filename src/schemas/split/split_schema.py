from pydantic import BaseModel

from src.schemas.user.user_schema import UserOutput


class SplitInput(BaseModel):
    user: UserOutput
    sort_by: str



class SplitOutput(BaseModel):
    user: UserOutput
    sort_by: str