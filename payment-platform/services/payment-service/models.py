"""Payment service database models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from shared.database.base import Base


class Payment(Base):
    """Payment record.
    
    Design decisions:
    - UUID primary key: globally unique, no sequential guessing
    - amount stored as integer (cents): avoids floating-point errors
    - idempotency_key: unique constraint prevents duplicate payments
    - Indexed on payer_id, payee_id, status for query performance
    """
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    payee_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="CREATED", index=True)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False, default="WALLET")
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_payments_payer_status", "payer_id", "status"),
        Index("ix_payments_created_at", "created_at"),
    )


class IdempotencyRecord(Base):
    """Idempotency key storage.
    
    Why database-level idempotency?
    Application-level checks (e.g., in-memory sets) fail because:
    1. Multiple instances don't share memory
    2. Race conditions between check and insert
    3. Instance restarts lose state
    
    Database UNIQUE constraint guarantees exactly-once at the storage level.
    Redis can accelerate lookups but is NOT the source of truth.
    """
    __tablename__ = "idempotency_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_body: Mapped[dict] = mapped_column(JSONB, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, default=201)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
