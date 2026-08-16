"""Auth service dependency injection."""
from services.auth_service.service import AuthServiceHandler


async def get_auth_service() -> AuthServiceHandler:
    return AuthServiceHandler()
