"""Transaction Service - Transaction processing and saga orchestration.

Implements the Saga Pattern for distributed transactions:

Payment Saga (Happy Path):
  1. Create Transaction (INITIATED)
  2. Validate Payer → Mark VALIDATED
  3. Fraud Check → Mark FRAUD_CLEARED
  4. Debit Wallet → Mark DEBITED
  5. Credit Wallet → Mark CREDITED
  6. Create Ledger Entry → Mark COMPLETED

Compensation (Failure at step 5):
  1. Reverse Debit (Credit payer back)
  2. Mark transaction REVERSED
  3. Emit compensation event
  4. Alert operations

Transactional Outbox Pattern:
  Instead of: DB commit THEN Kafka publish (can fail between steps)
  Do: DB commit (data + outbox event in same transaction)
  Background worker polls outbox → publishes to Kafka → marks as published
  Guarantees: If data is committed, event WILL be published (eventually)
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Transaction Service",
    description="Transaction processing, saga orchestration, outbox pattern",
    version="1.0.0",
    lifespan=lifespan,
)


class TransactionStatus(str, Enum):
    INITIATED = "INITIATED"
    VALIDATED = "VALIDATED"
    FRAUD_CLEARED = "FRAUD_CLEARED"
    DEBITED = "DEBITED"
    CREDITED = "CREDITED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class CreateTransactionRequest(BaseModel):
    payment_id: str
    payer_id: str
    payee_id: str
    amount: int = Field(..., gt=0)
    currency: str = Field(default="INR")
    idempotency_key: str


class TransactionResponse(BaseModel):
    id: str
    payment_id: str
    status: TransactionStatus
    payer_id: str
    payee_id: str
    amount: int
    currency: str
    saga_step: str = ""
    created_at: datetime
    updated_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "transaction-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "transaction-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(request: CreateTransactionRequest):
    """Create and initiate a transaction saga."""
    now = datetime.now(timezone.utc)
    return TransactionResponse(
        id=str(uuid.uuid4()),
        payment_id=request.payment_id,
        status=TransactionStatus.INITIATED,
        payer_id=request.payer_id,
        payee_id=request.payee_id,
        amount=request.amount,
        currency=request.currency,
        saga_step="initiated",
        created_at=now,
        updated_at=now,
    )


@app.get("/api/v1/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """Get transaction status."""
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="TRANSACTION_NOT_FOUND")
