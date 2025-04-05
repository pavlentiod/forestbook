from fastapi import Depends

from src.clients.forestlab_client import ForestLabClient
from src.config import settings



async def get_forestlab_client(token: str = Depends(settings.oauth2_scheme)) -> ForestLabClient:
    return ForestLabClient(base_url="http://127.0.0.1:8020", token=token)