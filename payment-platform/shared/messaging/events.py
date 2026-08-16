"""Base event definitions for Kafka messaging."""
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all domain events."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    source_service: str = ""
    payload: dict = Field(default_factory=dict)


class PaymentCreatedEvent(BaseEvent):
    """Emitted when a payment is created."""
    event_type: str = "payment.created"


class PaymentProcessingEvent(BaseEvent):
    """Emitted when payment processing begins."""
    event_type: str = "payment.processing"


class PaymentSucceededEvent(BaseEvent):
    """Emitted when a payment succeeds."""
    event_type: str = "payment.succeeded"


class PaymentFailedEvent(BaseEvent):
    """Emitted when a payment fails."""
    event_type: str = "payment.failed"


class PaymentRefundedEvent(BaseEvent):
    """Emitted when a payment is refunded."""
    event_type: str = "payment.refunded"


class NotificationRequestedEvent(BaseEvent):
    """Emitted to request a notification be sent."""
    event_type: str = "notification.requested"


class FraudCheckRequestedEvent(BaseEvent):
    """Emitted to request a fraud check."""
    event_type: str = "fraud.check.requested"
