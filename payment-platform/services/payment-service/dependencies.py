"""Dependency injection for payment service."""
from services.payment_service.service import PaymentServiceHandler


async def get_payment_service() -> PaymentServiceHandler:
    """Provide PaymentServiceHandler instance.
    
    In production, this would inject:
    - Database session from connection pool
    - Kafka producer
    - Redis client
    - Circuit breakers for external services
    """
    return PaymentServiceHandler()
