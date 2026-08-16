"""Wallet service database models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, BigInteger, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from shared.database.base import Base


class Wallet(Base):
    """Wallet model with optimistic locking via version column.
    
    Balance is stored in smallest currency unit (cents/paise) as BigInteger.
    NEVER use float/double for monetary values.
    
    Version column enables optimistic locking:
    UPDATE wallets SET balance = :new_balance, version = version + 1
    WHERE id = :id AND version = :expected_version
    If rows_affected == 0, another transaction modified it (retry).
    """
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class WalletTransaction(Base):
    """Individual wallet transaction for audit trail."""
    __tablename__ = "wallet_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_wallet_tx_wallet_created", "wallet_id", "created_at"),
    )
