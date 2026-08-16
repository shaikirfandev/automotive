"""Auth service business logic."""
import uuid
from datetime import datetime, timezone
from typing import Any

from shared.security import create_access_token, create_refresh_token, verify_token, hash_password, verify_password
from services.auth_service.schemas import (
    RegisterRequest,
    LoginResponse,
    TokenResponse,
    UserClaims,
    Role,
)


class AuthServiceHandler:
    """Authentication operations handler."""

    def __init__(self, db_session: Any = None, redis_client: Any = None, settings: Any = None):
        self._db = db_session
        self._redis = redis_client
        if settings:
            self._secret_key = settings.jwt_secret_key
            self._algorithm = settings.jwt_algorithm
        else:
            from services.auth_service.config import settings as default_settings
            self._secret_key = default_settings.jwt_secret_key
            self._algorithm = default_settings.jwt_algorithm

    async def register(self, request: RegisterRequest) -> LoginResponse:
        """Register new user and return tokens."""
        user_id = str(uuid.uuid4())
        # In production: hash password, store in DB
        _hashed = hash_password(request.password)

        token_data = {"sub": user_id, "email": request.email, "role": request.role.value}
        access_token = create_access_token(token_data, self._secret_key)
        refresh_token = create_refresh_token(token_data, self._secret_key)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            role=request.role,
        )

    async def login(self, username: str, password: str) -> LoginResponse:
        """Authenticate user credentials."""
        # In production: lookup user, verify password hash
        user_id = str(uuid.uuid4())
        token_data = {"sub": user_id, "email": username, "role": "user"}
        access_token = create_access_token(token_data, self._secret_key)
        refresh_token = create_refresh_token(token_data, self._secret_key)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            role=Role.USER,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """Issue new access token from valid refresh token."""
        payload = verify_token(refresh_token_str, self._secret_key)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        new_access = create_access_token(
            {"sub": payload["sub"], "email": payload.get("email", ""), "role": payload.get("role", "user")},
            self._secret_key,
        )
        return TokenResponse(access_token=new_access)

    async def verify(self, token: str) -> UserClaims | None:
        """Verify token and return claims."""
        try:
            payload = verify_token(token, self._secret_key)
            return UserClaims(
                user_id=payload["sub"],
                email=payload.get("email", ""),
                role=Role(payload.get("role", "user")),
                exp=payload["exp"],
            )
        except (ValueError, KeyError):
            return None
