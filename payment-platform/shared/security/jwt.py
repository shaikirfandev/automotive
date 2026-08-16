"""JWT token creation and verification."""
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt


def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 30,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_refresh_token(
    data: dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_days: int = 7,
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict[str, Any]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
