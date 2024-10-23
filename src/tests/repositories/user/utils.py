import bcrypt

from src.database.models.user.user import User


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

def exclude_password(user: User) -> dict:
    return {k:v for k,v in user.__dict__ if k != "hashed_password"}