from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.config import settings
from src.schemas.auth.auth_schema import Token
from src.services.auth.auth_service import AuthService
from src.services.auth.dependencies import get_auth_service, get_refresh_token

router = APIRouter()
endpoints = settings.api.auth

@router.post(endpoints.login.path, response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    return await auth_service.login(form_data)


@router.post(endpoints.refresh.path, response_model=Token)
async def refresh_token(
        token=Depends(get_refresh_token)
) -> Token:
    return token
