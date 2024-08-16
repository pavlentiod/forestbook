from pydantic import BaseModel


class Results(BaseModel):
    splits: dict
    routes: dict
    results: dict


