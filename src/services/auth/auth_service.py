from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user.user import User
from src.schemas.auth.auth_schema import UserSignIn, TokenInfo
from src.services.auth.dependencies import validate_classic_credentials
from src.services.auth.utils import validate_password, create_access_token, create_refresh_token
from src.services.user.user_service import UserService


class AuthService:
    """
    Service class for handling authentication and authorization.
    """

    def __init__(self, session: AsyncSession):
        self.session = session


    async def classic_auth(self, user: User = Depends(validate_classic_credentials)) -> TokenInfo:
        return TokenInfo(
            access_token=create_access_token(user),
            refresh_token=create_refresh_token(user)
        )

    async def refresh_jwt(self):
        pass
