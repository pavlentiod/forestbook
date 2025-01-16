from datetime import timedelta, datetime

import jwt
from fastapi import HTTPException
from starlette import status

from src.config import settings
from src.database.models.user.user import User
from src.schemas.user.user_schema import UserInDB

TOKEN_TYPE_FIELD = 'type'  # Field to indicate the token type in the payload
ACCESS_TOKEN_TYPE = 'access'  # Token type for access tokens
REFRESH_TOKEN_TYPE = 'refresh'  # Token type for refresh tokens


class JwtFactory:
    """
    Class for creating and managing JSON Web Tokens (JWTs).

    This class provides functionality to generate access and refresh tokens
    with specified payloads and expiration times. It also encodes and decodes JWTs
    for authentication and verification purposes.
    """

    def create_jwt(self, type: str, payload: dict,
                   expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
                   expire_timedelta: timedelta | None = None) -> str:
        """
        Create a JWT with the specified type and payload.

        Args:
            type (str): The type of token (e.g., 'access', 'refresh').
            payload (dict): The data to include in the JWT payload.
            expire_minutes (int): The default expiration time in minutes if `expire_timedelta` is not provided.
            expire_timedelta (timedelta | None): Optional custom expiration time as a timedelta object.

        Returns:
            str: The encoded JWT as a string.

        Example:
            >>> payload = {"user_id": 123}
            >>> token = self.create_jwt(type='access', payload=payload)
        """
        jwt_payload = {TOKEN_TYPE_FIELD: type}  # Add token type to payload
        jwt_payload.update(payload)  # Include additional payload data
        return self.encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
        )

    def create_access_token(self, user: UserInDB, scopes: list[str]) -> str:
        """
        Create an access token for a given user.

        Args:
            user (User): The user object containing necessary user information.
            scopes (list[str]): A list of scopes associated with the token.

        Returns:
            str: The encoded access token.

        Example:
            >>> token = self.create_access_token(user, scopes=["read", "write"])
        """
        jwt_payload = {
            "sub": user.email,  # Subject (user identifier)
            "username": user.email,  # Username
            "scopes": scopes,  # Scopes associated with the token
        }
        return self.create_jwt(
            type=ACCESS_TOKEN_TYPE,
            payload=jwt_payload,
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    def create_refresh_token(self, user: UserInDB, scopes: list[str]) -> str:
        """
        Create a refresh token for a given user.

        Args:
            user (UserInDB): The user object containing necessary user information.
            scopes (list[str]): A list of scopes associated with the token.

        Returns:
            str: The encoded refresh token.

        Example:
            >>> token = self.create_refresh_token(user, scopes=["articles:read_public"])
        """
        jwt_payload = {
            "sub": user.email,  # Subject (user identifier)
            "scopes": scopes,  # Scopes associated with the token
        }
        return self.create_jwt(
            type=REFRESH_TOKEN_TYPE,
            payload=jwt_payload,
            expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
        )

    def encode_jwt(self,
                   payload: dict,
                   private_key: str = settings.auth_jwt.private_key_path.read_text(),
                   algorithm: str = settings.auth_jwt.algorithm,
                   expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
                   expire_timedelta: timedelta | None = None) -> str:
        """
        Encode a JSON Web Token (JWT) with a given payload and expiration time.

        Args:
            payload (dict): The data to include in the JWT payload.
            private_key (str): The private key to sign the token.
            algorithm (str): The algorithm used for signing the JWT.
            expire_minutes (int): The default expiration time in minutes if `expire_timedelta` is not provided.
            expire_timedelta (timedelta | None): Optional custom expiration time as a timedelta object.

        Returns:
            str: The encoded JWT as a string.

        Example:
            >>> payload = {"user_id": 123}
            >>> token = self.encode_jwt(payload)
        """
        to_encode = payload.copy()
        now = datetime.utcnow()  # Current UTC time
        expire = now + expire_timedelta if expire_timedelta else now + timedelta(minutes=expire_minutes)

        to_encode.update(
            exp=expire,  # Expiration time
            iat=now,  # Issued-at time
        )
        encoded = jwt.encode(
            to_encode,
            private_key,
            algorithm=algorithm,
        )
        return encoded

    def decode_jwt(self,
                   token: str | bytes,
                   public_key: str = settings.auth_jwt.public_key_path.read_text(),
                   algorithm: str = settings.auth_jwt.algorithm) -> dict:
        """
        Decode a JSON Web Token (JWT) and verify its signature.

        Args:
            token (str | bytes): The JWT to decode.
            public_key (str): The public key used to verify the token.
            algorithm (str): The algorithm used for verifying the JWT.

        Returns:
            dict: The decoded JWT payload.

        Example:
            >>> decoded = self.decode_jwt(token)
        """
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=[algorithm],
        )
        return decoded

    def validate_token_type(self, payload: dict, type: str):
        token_type = payload.get('type')
        if token_type == type:
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"invalid token type {token_type!r} expected {type!r}",
            )
