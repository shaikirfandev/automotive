"""Reconciliation Service - Financial data verification and correction.

Purpose:
- Verify ledger integrity (Total Debits = Total Credits)
- Compare internal records with external payment provider records
- Detect and flag discrepancies
- Generate reconciliation reports
- Handle edge cases (orphaned transactions, partial completions)

Runs on schedule (cron) and on-demand.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from datetime import datetime, date, timezone
from enum import Enum
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Reconciliation Service",
    description="Financial reconciliation and integrity verification",
    version="1.0.0",
    lifespan=lifespan,
)


class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DISCREPANCY_FOUND = "DISCREPANCY_FOUND"


class ReconciliationRequest(BaseModel):
    start_date: date
    end_date: date
    type: str = Field(default="full", pattern="^(full|ledger|wallet|payment)$")


class ReconciliationResponse(BaseModel):
    id: str
    status: ReconciliationStatus
    start_date: date
    end_date: date
    total_transactions: int = 0
    matched: int = 0
    discrepancies: int = 0
    created_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "reconciliation-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "reconciliation-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/reconciliation/run", response_model=ReconciliationResponse, status_code=201)
async def run_reconciliation(request: ReconciliationRequest):
    """Trigger a reconciliation run."""
    return ReconciliationResponse(
        id=str(uuid.uuid4()),
        status=ReconciliationStatus.PENDING,
        start_date=request.start_date,
        end_date=request.end_date,
        created_at=datetime.now(timezone.utc),
    )
