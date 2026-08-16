"""Account Service - Financial account management."""
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


app = FastAPI(title="Account Service", version="1.0.0", lifespan=lifespan)


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    WALLET = "WALLET"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class CreateAccountRequest(BaseModel):
    user_id: str
    account_type: AccountType
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")


class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_type: AccountType
    status: AccountStatus
    currency: str
    created_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "account-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/accounts", response_model=AccountResponse, status_code=201)
async def create_account(request: CreateAccountRequest):
    return AccountResponse(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        account_type=request.account_type,
        status=AccountStatus.ACTIVE,
        currency=request.currency,
        created_at=datetime.now(timezone.utc),
    )
