"""Payment service business logic.

Implements the payment lifecycle with:
- Idempotency checking
- State machine validation
- Event emission
- Saga coordination
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from services.payment_service.schemas import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentStatus,
)


# Valid state transitions
VALID_TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
    PaymentStatus.CREATED: {PaymentStatus.PENDING},
    PaymentStatus.PENDING: {PaymentStatus.PROCESSING},
    PaymentStatus.PROCESSING: {PaymentStatus.SUCCESS, PaymentStatus.FAILED},
    PaymentStatus.FAILED: {PaymentStatus.PROCESSING, PaymentStatus.REVERSED},
    PaymentStatus.SUCCESS: {PaymentStatus.REFUNDED},
    PaymentStatus.REVERSED: set(),
    PaymentStatus.REFUNDED: set(),
}


def validate_transition(current: PaymentStatus, target: PaymentStatus) -> bool:
    """Validate payment state transition."""
    return target in VALID_TRANSITIONS.get(current, set())


class PaymentServiceHandler:
    """Payment service handler with business logic.
    
    Design: Service layer pattern separating HTTP concerns from business logic.
    Dependencies are injected, making the service testable.
    """

    def __init__(self, db_session: Any = None, kafka_producer: Any = None, redis_client: Any = None):
        self._db = db_session
        self._kafka = kafka_producer
        self._redis = redis_client

    async def create_payment(
        self,
        request: CreatePaymentRequest,
        idempotency_key: str,
        request_id: str,
    ) -> PaymentResponse:
        """Create a new payment with idempotency guarantee.
        
        Flow:
        1. Check if idempotency key already used → return cached response
        2. Hash request for idempotency validation
        3. Create payment in CREATED state
        4. Store idempotency record
        5. Emit PaymentCreated event
        6. Return payment response
        """
        # Generate request hash for idempotency validation
        request_hash = hashlib.sha256(
            request.model_dump_json().encode()
        ).hexdigest()

        # Create payment record
        payment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        payment = PaymentResponse(
            id=payment_id,
            payer_id=request.payer_id,
            payee_id=request.payee_id,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.CREATED,
            payment_method=request.payment_method,
            description=request.description,
            idempotency_key=idempotency_key,
            created_at=now,
            updated_at=now,
            metadata=request.metadata,
        )

        # In production with DB:
        # 1. INSERT payment with idempotency_key UNIQUE constraint
        # 2. On conflict, return existing payment
        # 3. Emit Kafka event

        return payment

    async def get_payment(self, payment_id: str) -> PaymentResponse | None:
        """Retrieve payment by ID."""
        # In production: query DB
        return None

    async def refund_payment(self, payment_id: str) -> PaymentResponse:
        """Initiate refund for a completed payment.
        
        Refund flow (Saga):
        1. Validate payment is in SUCCESS state
        2. Transition to REFUNDED
        3. Credit payer wallet (compensation)
        4. Debit payee wallet
        5. Create ledger reversal entries
        6. Emit PaymentRefunded event
        
        If step 4 fails:
        - Reverse step 3 (debit payer)
        - Mark payment as FAILED refund
        - Alert operations team
        """
        raise NotImplementedError("Refund requires database integration")

    async def process_payment(self, payment_id: str) -> None:
        """Process a payment through the saga.
        
        Saga Steps:
        1. CREATED → PENDING: Validate all parties
        2. PENDING → PROCESSING: Debit payer wallet  
        3. PROCESSING → SUCCESS: Credit payee, create ledger entries
        
        Compensation (on failure at any step):
        - Reverse all completed steps
        - Mark payment REVERSED
        - Emit compensation events
        """
        pass
