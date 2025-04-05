from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.config import settings
from src.database.models.user.user import User
from src.repositories.subscription.subscription_repository import SubscriptionRepository
from src.schemas.auth.auth_schema import Token
from src.schemas.subscription.subscrption_schema import UserSubscriptionOutput
from src.schemas.user.user_schema import UserInDB, UserPreview
from src.services.auth.subservices.jwt_factory import JwtFactory
from src.services.auth.utils import validate_password
from src.services.user.user_service import UserService

ACCESS_TOKEN_TYPE = 'access'  # Token type for access tokens
REFRESH_TOKEN_TYPE = 'refresh'  # Token type for refresh tokens


class AuthService:
    """
    Service class for handling authentication and authorization.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.jwt_factory = JwtFactory()

    async def authenticate_user(self, email: str, password: str) -> UserInDB:
        """
        Authenticate the user using email and password.

        Args:
            email (str): User email.
            password (str): User password.

        Returns:
            User: Authenticated user.

        Raises:
            HTTPException: If authentication fails.
        """
        user_service = UserService(self.session)
        user = await user_service.get_by_email(email)
        if not user or not validate_password(password=password, hashed_password=user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return UserInDB(**user.model_dump())

    async def get_current_user(self, token: str = Depends(settings.oauth2_scheme)) -> UserPreview:
        """
        Retrieve the current user from the access token.

        Args:
            token (str): The JWT access token.

        Returns:
            User: The current authenticated user.

        Raises:
            HTTPException: If token validation or user retrieval fails.
        """
        try:
            payload = self.jwt_factory.decode_jwt(token=token)
            self.jwt_factory.validate_token_type(payload, ACCESS_TOKEN_TYPE)
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            scopes = payload.get("scopes", [])
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}"
            )

        user_service = UserService(self.session)
        user = await user_service.get_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return UserInDB(**user.model_dump())


    async def login(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        user: UserInDB = await self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Получаем подписочные scopes
        sub_repo = SubscriptionRepository(self.session)
        subscription: UserSubscriptionOutput = await sub_repo.get_user_active_subscription(user.id)

        # Объединяем scopes из формы и из подписки
        subscription_scopes = subscription.plan.scopes if subscription else []
        all_scopes = list(set(form_data.scopes + subscription_scopes))

        # Генерируем токены
        access_token = self.jwt_factory.create_access_token(user, all_scopes)
        refresh_token = self.jwt_factory.create_refresh_token(user, all_scopes)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=all_scopes
        )

    async def refresh(self, token) -> Token:
        pass