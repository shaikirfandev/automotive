"""Payment Service - Handles payment lifecycle management.

This service manages the complete payment flow:
1. Payment creation with idempotency
2. Validation (user, account, fraud check)
3. Processing (debit wallet, create ledger entry)
4. State management (CREATED → PENDING → PROCESSING → SUCCESS/FAILED)
5. Event emission for downstream consumers
"""
import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from services.payment_service.config import settings
from services.payment_service.schemas import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentListResponse,
    ErrorResponse,
)
from services.payment_service.service import PaymentServiceHandler
from services.payment_service.dependencies import get_payment_service


# Metrics
PAYMENT_REQUESTS = Counter(
    "payment_requests_total", "Total payment requests", ["method", "status"]
)
PAYMENT_LATENCY = Histogram(
    "payment_request_duration_seconds", "Payment request latency"
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - startup and shutdown."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Payment Service",
    description="Handles payment lifecycle - creation, processing, refunds",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics."""
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    PAYMENT_LATENCY.observe(duration)
    PAYMENT_REQUESTS.labels(method=request.method, status=response.status_code).inc()
    return response


@app.get("/health")
async def health_check():
    """Liveness probe - service is running."""
    return {"status": "healthy", "service": "payment-service"}


@app.get("/readiness")
async def readiness_check():
    """Readiness probe - service can accept traffic."""
    # In production: check DB, Redis, Kafka connectivity
    return {"status": "ready", "service": "payment-service"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post(
    "/api/v1/payments",
    response_model=PaymentResponse,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "Duplicate payment"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
async def create_payment(
    request: CreatePaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4()), alias="X-Request-ID"),
    payment_service: PaymentServiceHandler = Depends(get_payment_service),
):
    """Create a new payment.
    
    Idempotent: sending the same Idempotency-Key returns the original response.
    
    Payment Flow:
    1. Check idempotency key
    2. Validate payer/payee
    3. Create payment record (CREATED)
    4. Initiate async processing
    5. Return payment details
    """
    result = await payment_service.create_payment(
        request=request,
        idempotency_key=idempotency_key,
        request_id=x_request_id,
    )
    return result


@app.get("/api/v1/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    payment_service: PaymentServiceHandler = Depends(get_payment_service),
):
    """Get payment details by ID."""
    result = await payment_service.get_payment(payment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@app.post("/api/v1/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: str,
    payment_service: PaymentServiceHandler = Depends(get_payment_service),
):
    """Initiate a refund for a completed payment."""
    result = await payment_service.refund_payment(payment_id)
    return result


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.detail if isinstance(exc.detail, str) else "ERROR",
                "message": str(exc.detail),
                "request_id": request.headers.get("X-Request-ID", ""),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        },
    )
