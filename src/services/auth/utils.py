import bcrypt


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
