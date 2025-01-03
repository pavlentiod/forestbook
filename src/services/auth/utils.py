import uuid
from datetime import datetime, timedelta

import bcrypt
import jwt

from src.config import settings
from src.database.models.user.user import User


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
) -> str:
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
        >>> token = encode_jwt(payload)
    """
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,  # Expiration time
        iat=now,     # Issued-at time
        jti=str(uuid.uuid4())  # Unique identifier for the token
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    """
    Decode a JSON Web Token (JWT) and verify its signature.

    Args:
        token (str | bytes): The JWT to decode.
        public_key (str): The public key used to verify the token.
        algorithm (str): The algorithm used for verifying the JWT.

    Returns:
        dict: The decoded JWT payload.

    Example:
        >>> decoded = decode_jwt(token)
    """
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    """
    Validate a plaintext password against a hashed password.

    Args:
        password (str): The plaintext password to validate.
        hashed_password (bytes): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.

    Example:
        >>> is_valid = validate_password("user_password", hashed_password)
    """
    return bcrypt.checkpw(
        password=password.encode(),  # Encode plaintext password to bytes
        hashed_password=hashed_password,
    )


TOKEN_TYPE_FIELD = 'type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": user.email,
        "username": user.email,
        "access": user.access
    }
    return create_jwt(type=ACCESS_TOKEN_TYPE,
                      payload=jwt_payload,
                      expire_minutes = settings.auth_jwt.access_token_expire_minutes)


def create_refresh_token(user: User) -> str:
    jwt_payload = {
        "sub": user.email,
    }
    return create_jwt(type=REFRESH_TOKEN_TYPE,
                      payload=jwt_payload,
                      expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days))


def create_jwt(type, payload,
               expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
               expire_timedelta: timedelta | None = None):
    jwt_payload = {TOKEN_TYPE_FIELD: type}
    jwt_payload.update(payload)
    return encode_jwt(payload=jwt_payload,
                                 expire_minutes=expire_minutes,
                                 expire_timedelta=expire_timedelta)
