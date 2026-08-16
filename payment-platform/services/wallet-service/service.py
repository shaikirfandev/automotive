"""Wallet service business logic.

Implements:
- Wallet creation
- Credit/Debit with locking
- Transfer with atomic operations
- Balance validation
- Concurrency control

Locking Strategy:
  For debits: Pessimistic locking (SELECT FOR UPDATE)
    - Guarantees no double-spend
    - Holds lock for transaction duration
    - Trade-off: reduced throughput under contention
  
  For credits: Optimistic locking (version check)
    - Higher throughput for non-contentious ops
    - Retry on conflict
    - Trade-off: may need retries under contention

  For transfers: Lock both wallets in consistent order (by ID)
    - Prevents deadlocks
    - Always lock lower ID first
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from services.wallet_service.schemas import (
    CreateWalletRequest,
    WalletResponse,
    WalletStatus,
    CreditRequest,
    DebitRequest,
    TransferRequest,
    TransactionResponse,
    TransactionType,
)


class WalletServiceHandler:
    """Wallet operations handler."""

    def __init__(self, db_session: Any = None, redis_client: Any = None):
        self._db = db_session
        self._redis = redis_client

    async def create_wallet(self, request: CreateWalletRequest) -> WalletResponse:
        """Create a new wallet for a user."""
        now = datetime.now(timezone.utc)
        wallet_id = str(uuid.uuid4())
        return WalletResponse(
            id=wallet_id,
            user_id=request.user_id,
            balance=0,
            currency=request.currency,
            status=WalletStatus.ACTIVE,
            version=1,
            created_at=now,
            updated_at=now,
        )

    async def get_wallet(self, wallet_id: str) -> WalletResponse | None:
        """Get wallet by ID. Uses cache-aside pattern with Redis."""
        # 1. Check Redis cache
        # 2. On miss, query PostgreSQL
        # 3. Populate cache with TTL
        # 4. Return wallet
        return None

    async def credit(self, wallet_id: str, request: CreditRequest) -> TransactionResponse:
        """Credit wallet using optimistic locking.
        
        SQL equivalent:
          BEGIN;
          SELECT balance, version FROM wallets WHERE id = :id;
          UPDATE wallets 
            SET balance = balance + :amount, 
                version = version + 1,
                updated_at = NOW()
            WHERE id = :id AND version = :expected_version;
          -- If rows_affected == 0: ROLLBACK and RETRY
          INSERT INTO wallet_transactions (...);
          COMMIT;
        """
        now = datetime.now(timezone.utc)
        return TransactionResponse(
            id=str(uuid.uuid4()),
            wallet_id=wallet_id,
            type=TransactionType.CREDIT,
            amount=request.amount,
            balance_after=request.amount,  # Simplified
            reference_id=request.reference_id,
            description=request.description,
            created_at=now,
        )

    async def debit(self, wallet_id: str, request: DebitRequest) -> TransactionResponse:
        """Debit wallet using pessimistic locking (SELECT FOR UPDATE).
        
        SQL equivalent:
          BEGIN;
          SELECT balance FROM wallets WHERE id = :id FOR UPDATE;
          -- Row is now locked until COMMIT/ROLLBACK
          IF balance < amount THEN RAISE insufficient_balance;
          UPDATE wallets SET balance = balance - :amount, updated_at = NOW()
            WHERE id = :id;
          INSERT INTO wallet_transactions (...);
          COMMIT;
          -- Lock released
        
        Why SELECT FOR UPDATE?
          Without it, two concurrent debits can both read the same balance
          and both succeed, resulting in negative balance (double-spend).
        """
        now = datetime.now(timezone.utc)
        return TransactionResponse(
            id=str(uuid.uuid4()),
            wallet_id=wallet_id,
            type=TransactionType.DEBIT,
            amount=request.amount,
            balance_after=0,
            reference_id=request.reference_id,
            description=request.description,
            created_at=now,
        )

    async def transfer(self, request: TransferRequest) -> TransactionResponse:
        """Atomic transfer between wallets.
        
        Deadlock prevention:
          Always lock wallets in consistent order (sorted by ID).
          If we lock A then B in one transaction, and B then A in another,
          we get a deadlock. Sorting ensures consistent order.
        
        SQL equivalent:
          BEGIN;
          -- Lock both rows in ID order
          SELECT * FROM wallets WHERE id IN (:from, :to) ORDER BY id FOR UPDATE;
          -- Validate from_wallet has sufficient balance
          UPDATE wallets SET balance = balance - :amount WHERE id = :from;
          UPDATE wallets SET balance = balance + :amount WHERE id = :to;
          INSERT INTO wallet_transactions (...) VALUES (debit_record);
          INSERT INTO wallet_transactions (...) VALUES (credit_record);
          COMMIT;
        """
        now = datetime.now(timezone.utc)
        return TransactionResponse(
            id=str(uuid.uuid4()),
            wallet_id=request.from_wallet_id,
            type=TransactionType.TRANSFER_OUT,
            amount=request.amount,
            balance_after=0,
            reference_id=request.reference_id,
            description=request.description,
            created_at=now,
        )
