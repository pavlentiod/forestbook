from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jwt import InvalidTokenError
from pydantic import ValidationError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.config import settings
from src.database import db_helper
from src.schemas.auth.auth_schema import TokenData, Token
from src.schemas.user.user_schema import UserInDB, UserPreview
from src.services.auth.auth_service import AuthService
from src.services.auth.subservices.jwt_factory import JwtFactory


def get_auth_service(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return AuthService(session=session)


async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(settings.oauth2_scheme)],
        auth_service: AuthService = Depends(get_auth_service)
) -> UserPreview:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = auth_service.jwt_factory.decode_jwt(token)
        username: str = payload["sub"]
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user: UserPreview = await auth_service.get_current_user(token)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def check_scopes(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(settings.oauth2_scheme)]
):
    print(security_scopes.scopes)
    return True

async def get_current_active_user(
        current_user: Annotated[UserInDB, Security(get_current_user)],
) -> UserPreview:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_token_payload(
        token: Annotated[str, Depends(settings.oauth2_scheme)]
) -> dict:
    jwt_factory = JwtFactory()
    return jwt_factory.decode_jwt(token)


async def get_refresh_token(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
        payload: Annotated[dict, Depends(get_current_token_payload)]
) -> Token:
    jwt_factory = JwtFactory()
    jwt_factory.validate_token_type(payload, "refresh")
    scopes = payload.get("scopes")
    access_token = jwt_factory.create_access_token(current_user, scopes)
    return Token(access_token=access_token, scopes=scopes)
