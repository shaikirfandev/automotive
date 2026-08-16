"""User service configuration."""
from shared.config import BaseServiceSettings


class UserServiceSettings(BaseServiceSettings):
    service_name: str = "user-service"
    port: int = 8002


settings = UserServiceSettings()
