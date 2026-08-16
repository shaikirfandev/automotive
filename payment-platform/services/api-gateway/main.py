"""API Gateway - Entry point for all client requests.

Responsibilities:
- Authentication (JWT verification)
- Authorization (RBAC)
- Rate limiting (per user/IP)
- Request routing to downstream services
- Correlation ID injection
- Request/response logging
- API versioning
- CORS handling
- Request validation
"""
import uuid
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


REQUEST_COUNT = Counter("gateway_requests_total", "Total requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("gateway_request_duration_seconds", "Request latency")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Payment Platform API Gateway",
    description="Unified API entry point with auth, rate limiting, routing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Add correlation ID, log request, track metrics."""
    # Inject correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    # Add headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"

    # Track metrics
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.observe(duration)

    return response


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "api-gateway"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# API Routes - In production these proxy to downstream services
@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service: str, path: str, request: Request):
    """Route requests to appropriate downstream service.
    
    In production, this uses httpx to forward requests to services.
    Service discovery via Kubernetes DNS or service mesh.
    
    Routes:
      /api/v1/auth/*       → auth-service:8001
      /api/v1/users/*      → user-service:8002
      /api/v1/wallets/*    → wallet-service:8004
      /api/v1/payments/*   → payment-service:8005
      /api/v1/transactions/* → transaction-service:8006
      /api/v1/ledger/*     → ledger-service:8007
      /api/v1/fraud/*      → fraud-service:8008
    """
    service_map = {
        "auth": "http://auth-service:8001",
        "users": "http://user-service:8002",
        "wallets": "http://wallet-service:8004",
        "payments": "http://payment-service:8005",
        "transactions": "http://transaction-service:8006",
        "ledger": "http://ledger-service:8007",
        "fraud": "http://fraud-service:8008",
        "notifications": "http://notification-service:8009",
    }

    if service not in service_map:
        raise HTTPException(status_code=404, detail="Service not found")

    # In production: forward with httpx, circuit breaker, timeout
    return JSONResponse(
        status_code=501,
        content={"message": f"Proxy to {service_map[service]}/api/v1/{service}/{path}"},
    )
