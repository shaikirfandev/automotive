"""Merchant Service - Merchant onboarding and management."""
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


app = FastAPI(title="Merchant Service", version="1.0.0", lifespan=lifespan)


class MerchantStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class CreateMerchantRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str
    business_type: str
    bank_account: str = ""


class MerchantResponse(BaseModel):
    id: str
    name: str
    email: str
    status: MerchantStatus
    created_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "merchant-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/merchants", response_model=MerchantResponse, status_code=201)
async def create_merchant(request: CreateMerchantRequest):
    return MerchantResponse(
        id=str(uuid.uuid4()),
        name=request.name,
        email=request.email,
        status=MerchantStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
