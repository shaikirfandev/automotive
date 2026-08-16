"""Wallet Service - Manages user wallets and balance operations.

Critical design considerations:
- All balance operations use SELECT FOR UPDATE to prevent race conditions
- Double-spend prevention through pessimistic locking
- Atomic debit/credit operations within database transactions
- Event sourcing for balance audit trail

Race Condition Example (without locking):
  User balance = 1000
  Request A reads 1000, spends 800 → balance should be 200
  Request B reads 1000, spends 700 → balance should be 300
  Without locking, both succeed → 1500 spent from 1000!

Solution: SELECT FOR UPDATE locks the row during the transaction.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from services.wallet_service.config import settings
from services.wallet_service.schemas import (
    CreateWalletRequest,
    WalletResponse,
    CreditRequest,
    DebitRequest,
    TransferRequest,
    TransactionResponse,
)
from services.wallet_service.service import WalletServiceHandler
from services.wallet_service.dependencies import get_wallet_service


WALLET_OPS = Counter("wallet_operations_total", "Wallet operations", ["operation", "status"])
WALLET_LATENCY = Histogram("wallet_operation_duration_seconds", "Wallet operation latency")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Wallet Service",
    description="Manages user wallets - balance, credit, debit, transfer",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "wallet-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "wallet-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/wallets", response_model=WalletResponse, status_code=201)
async def create_wallet(
    request: CreateWalletRequest,
    wallet_service: WalletServiceHandler = Depends(get_wallet_service),
):
    """Create a new wallet for a user."""
    return await wallet_service.create_wallet(request)


@app.get("/api/v1/wallets/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    wallet_service: WalletServiceHandler = Depends(get_wallet_service),
):
    """Get wallet details including balance."""
    result = await wallet_service.get_wallet(wallet_id)
    if not result:
        raise HTTPException(status_code=404, detail="WALLET_NOT_FOUND")
    return result


@app.post("/api/v1/wallets/{wallet_id}/credit", response_model=TransactionResponse)
async def credit_wallet(
    wallet_id: str,
    request: CreditRequest,
    wallet_service: WalletServiceHandler = Depends(get_wallet_service),
):
    """Credit (add money to) a wallet.
    
    Uses optimistic locking with version check.
    """
    return await wallet_service.credit(wallet_id, request)


@app.post("/api/v1/wallets/{wallet_id}/debit", response_model=TransactionResponse)
async def debit_wallet(
    wallet_id: str,
    request: DebitRequest,
    wallet_service: WalletServiceHandler = Depends(get_wallet_service),
):
    """Debit (remove money from) a wallet.
    
    Uses SELECT FOR UPDATE for pessimistic locking.
    Validates sufficient balance before debit.
    """
    return await wallet_service.debit(wallet_id, request)


@app.post("/api/v1/wallets/transfer", response_model=TransactionResponse)
async def transfer(
    request: TransferRequest,
    wallet_service: WalletServiceHandler = Depends(get_wallet_service),
):
    """Transfer between wallets atomically."""
    return await wallet_service.transfer(request)
