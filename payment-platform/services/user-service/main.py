"""User Service - User profile and account management."""
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="User Service",
    description="User profile management, KYC, preferences",
    version="1.0.0",
    lifespan=lifespan,
)


class CreateUserRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(default="", max_length=15)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    is_verified: bool = False
    created_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "user-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/users", response_model=UserResponse, status_code=201)
async def create_user(request: CreateUserRequest):
    """Create a new user profile."""
    from datetime import timezone
    return UserResponse(
        id=str(uuid.uuid4()),
        email=request.email,
        full_name=request.full_name,
        phone=request.phone,
        created_at=datetime.now(timezone.utc),
    )


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID."""
    raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
