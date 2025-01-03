from fastapi import HTTPException

from src.schemas.auth.auth_schema import UserSignIn, TokenInfo
from src.services.auth.utils import validate_password
from src.services.user.user_service import UserService


async def validate_classic_credentials(self, data: UserSignIn) -> TokenInfo:
    user_service = UserService(self.session)
    user = await user_service.get_by_email(data.email)
    if validate_password(password=data.password, hashed_password=user.hashed_password) and user.is_active:
        return user
    raise HTTPException(status_code=401, detail="Authentication error")

