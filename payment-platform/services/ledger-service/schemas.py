"""Ledger service schemas."""
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class EntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class CreateLedgerEntryRequest(BaseModel):
    """Create a double-entry ledger record.
    
    Both debit_account and credit_account must be specified.
    Amount must be positive.
    Transaction reference links to the originating payment.
    """
    transaction_reference: str = Field(..., description="Payment/transaction ID")
    debit_account_id: str = Field(..., description="Account being debited")
    credit_account_id: str = Field(..., description="Account being credited")
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")
    description: str = Field(default="")
    idempotency_key: str = Field(..., description="Prevents duplicate entries")


class LedgerEntryResponse(BaseModel):
    """Response containing both debit and credit entries."""
    id: str
    transaction_reference: str
    debit_entry_id: str
    credit_entry_id: str
    debit_account_id: str
    credit_account_id: str
    amount: int
    currency: str
    description: str
    created_at: datetime


class LedgerBalanceResponse(BaseModel):
    """Account balance derived from ledger entries."""
    account_id: str
    total_debits: int
    total_credits: int
    net_balance: int
    currency: str
    entry_count: int
