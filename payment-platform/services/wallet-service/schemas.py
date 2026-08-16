"""Wallet service schemas."""
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class WalletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"


class CreateWalletRequest(BaseModel):
    user_id: str = Field(..., description="Owner user ID")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")


class WalletResponse(BaseModel):
    id: str
    user_id: str
    balance: int = Field(..., description="Balance in smallest currency unit")
    currency: str
    status: WalletStatus
    version: int = Field(..., description="Optimistic lock version")
    created_at: datetime
    updated_at: datetime


class CreditRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to credit in smallest unit")
    reference_id: str = Field(..., description="External reference for idempotency")
    description: str = Field(default="")


class DebitRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to debit in smallest unit")
    reference_id: str = Field(..., description="External reference for idempotency")
    description: str = Field(default="")


class TransferRequest(BaseModel):
    from_wallet_id: str
    to_wallet_id: str
    amount: int = Field(..., gt=0)
    reference_id: str
    description: str = Field(default="")


class TransactionResponse(BaseModel):
    id: str
    wallet_id: str
    type: TransactionType
    amount: int
    balance_after: int
    reference_id: str
    description: str
    created_at: datetime
