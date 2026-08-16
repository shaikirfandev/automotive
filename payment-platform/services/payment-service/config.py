"""Payment service configuration."""
from shared.config import BaseServiceSettings


class PaymentServiceSettings(BaseServiceSettings):
    """Payment service specific settings."""
    service_name: str = "payment-service"
    port: int = 8005
    
    # Payment specific
    max_payment_amount: int = 1000000_00  # in cents
    min_payment_amount: int = 1  # in cents
    payment_timeout_seconds: int = 30
    idempotency_key_ttl_hours: int = 24


settings = PaymentServiceSettings()
