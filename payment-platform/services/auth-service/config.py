"""Auth service configuration."""
from shared.config import BaseServiceSettings


class AuthServiceSettings(BaseServiceSettings):
    service_name: str = "auth-service"
    port: int = 8001
    login_rate_limit: int = 5
    account_lockout_threshold: int = 10
    account_lockout_duration_minutes: int = 30


settings = AuthServiceSettings()
