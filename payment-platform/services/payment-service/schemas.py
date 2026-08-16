"""Payment service Pydantic schemas.

All monetary values are in the smallest currency unit (e.g., cents/paise).
Never use float for money - always use int (cents) or Decimal.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class PaymentStatus(str, Enum):
    """Payment lifecycle states.
    
    Valid transitions:
      CREATED → PENDING → PROCESSING → SUCCESS
      CREATED → PENDING → PROCESSING → FAILED
      SUCCESS → REFUNDED
      PROCESSING → FAILED → (retry) → PROCESSING
      Any → REVERSED (compensation)
    """
    CREATED = "CREATED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    WALLET = "WALLET"
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"


class CreatePaymentRequest(BaseModel):
    """Request to create a new payment."""
    payer_id: str = Field(..., description="ID of the user making payment")
    payee_id: str = Field(..., description="ID of the user receiving payment")
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit (cents/paise)")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")
    payment_method: PaymentMethod = PaymentMethod.WALLET
    description: str = Field(default="", max_length=500)
    metadata: dict = Field(default_factory=dict)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        if v > 1000000_00:
            raise ValueError("Amount exceeds maximum limit")
        return v


class PaymentResponse(BaseModel):
    """Payment response schema."""
    id: str
    payer_id: str
    payee_id: str
    amount: int
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    description: str
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(default_factory=dict)


class PaymentListResponse(BaseModel):
    """Paginated list of payments."""
    payments: list[PaymentResponse]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: dict = Field(
        ...,
        examples=[{
            "code": "INSUFFICIENT_BALANCE",
            "message": "Insufficient account balance",
            "request_id": "req_123",
            "timestamp": "2024-01-01T00:00:00Z",
        }]
    )
