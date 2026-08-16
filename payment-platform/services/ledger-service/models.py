"""Ledger service database models.

Design: Append-only ledger entries. Never update or delete entries.
Corrections are made via reversal entries.

Performance: Indexed on account_id and transaction_reference.
Balance calculation: SUM(credits) - SUM(debits) per account.
For high-throughput: maintain materialized balance with periodic reconciliation.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from shared.database.base import Base


class LedgerEntry(Base):
    """Individual ledger entry (one side of double-entry)."""
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_reference: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DEBIT or CREDIT
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    idempotency_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_ledger_account_type", "account_id", "entry_type"),
        Index("ix_ledger_txn_ref", "transaction_reference"),
    )
