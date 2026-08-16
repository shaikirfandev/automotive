"""Base service configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    """Base settings shared across all services."""

    # Service
    service_name: str = "unknown-service"
    service_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/payments"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "default-group"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Observability
    otlp_endpoint: str = "http://localhost:4317"
    log_level: str = "INFO"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}
