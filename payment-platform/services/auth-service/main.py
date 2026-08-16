"""Authentication Service - JWT-based auth with OAuth2 patterns.

Security implementation:
- Passwords hashed with bcrypt (cost factor 12)
- JWT access tokens (short-lived, 30 min)
- JWT refresh tokens (longer-lived, 7 days)
- Rate limiting on login endpoints (brute-force protection)
- Token blacklisting for logout
- RBAC via token claims
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from services.auth_service.schemas import (
    RegisterRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserClaims,
)
from services.auth_service.service import AuthServiceHandler
from services.auth_service.dependencies import get_auth_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="Authentication Service",
    description="Handles user authentication, JWT tokens, OAuth2",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "auth-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/auth/register", response_model=LoginResponse, status_code=201)
async def register(
    request: RegisterRequest,
    auth_service: AuthServiceHandler = Depends(get_auth_service),
):
    """Register a new user and return tokens."""
    return await auth_service.register(request)


@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceHandler = Depends(get_auth_service),
):
    """Authenticate user and return JWT tokens.
    
    Rate limited: 5 attempts per minute per IP.
    After 10 failed attempts, account is temporarily locked.
    """
    return await auth_service.login(form_data.username, form_data.password)


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    auth_service: AuthServiceHandler = Depends(get_auth_service),
):
    """Refresh an access token using a valid refresh token."""
    return await auth_service.refresh_token(request.refresh_token)


@app.post("/api/v1/auth/logout", status_code=204)
async def logout(
    auth_service: AuthServiceHandler = Depends(get_auth_service),
):
    """Logout - blacklist current tokens."""
    return None


@app.get("/api/v1/auth/verify", response_model=UserClaims)
async def verify_token(
    token: str,
    auth_service: AuthServiceHandler = Depends(get_auth_service),
):
    """Verify a JWT token and return claims. Used by API Gateway."""
    claims = await auth_service.verify(token)
    if not claims:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    return claims
