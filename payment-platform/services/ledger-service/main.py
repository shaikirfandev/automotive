"""Ledger Service - Double-entry bookkeeping for financial correctness.

Double-Entry Accounting Principle:
  Every financial transaction creates TWO entries:
  - A DEBIT entry (money leaving one account)
  - A CREDIT entry (money entering another account)
  
  Invariant: Total Debits = Total Credits (ALWAYS)
  
  This ensures:
  1. No money is created or destroyed
  2. Every transaction is traceable
  3. Reconciliation is possible
  4. Audit trail is complete

Example: User A pays User B ₹100
  Entry 1: DEBIT  A's wallet account  ₹100
  Entry 2: CREDIT B's wallet account  ₹100
  
  Sum of all debits = Sum of all credits ✓
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from services.ledger_service.config import settings
from services.ledger_service.schemas import (
    CreateLedgerEntryRequest,
    LedgerEntryResponse,
    LedgerBalanceResponse,
)
from services.ledger_service.service import LedgerServiceHandler
from services.ledger_service.dependencies import get_ledger_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Ledger Service",
    description="Double-entry ledger for financial transaction recording",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ledger-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "ledger-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/ledger/entries", response_model=LedgerEntryResponse, status_code=201)
async def create_entry(
    request: CreateLedgerEntryRequest,
    ledger_service: LedgerServiceHandler = Depends(get_ledger_service),
):
    """Create a double-entry ledger record.
    
    Both debit and credit entries are created atomically.
    The invariant Total Debits = Total Credits is maintained.
    """
    return await ledger_service.create_entry(request)


@app.get("/api/v1/ledger/balance/{account_id}", response_model=LedgerBalanceResponse)
async def get_balance(
    account_id: str,
    ledger_service: LedgerServiceHandler = Depends(get_ledger_service),
):
    """Get ledger balance for an account."""
    return await ledger_service.get_balance(account_id)


@app.get("/api/v1/ledger/verify")
async def verify_integrity(
    ledger_service: LedgerServiceHandler = Depends(get_ledger_service),
):
    """Verify ledger integrity: Total Debits must equal Total Credits."""
    is_valid = await ledger_service.verify_integrity()
    return {"integrity": "valid" if is_valid else "CORRUPTED", "balanced": is_valid}
