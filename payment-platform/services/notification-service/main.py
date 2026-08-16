"""Notification Service - Email, SMS, Push notifications.

Design: Event-driven, consumes from Kafka topics.
Non-critical: failure here should NEVER fail a payment.
Uses circuit breaker for external providers (email/SMS gateways).

Graceful degradation:
- If notification fails, payment remains successful
- Failed notifications are retried via dead-letter queue
- After max retries, alert operations team
"""
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


app = FastAPI(
    title="Notification Service",
    description="Multi-channel notification delivery",
    version="1.0.0",
    lifespan=lifespan,
)


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class SendNotificationRequest(BaseModel):
    user_id: str
    type: NotificationType
    template: str
    data: dict = Field(default_factory=dict)
    priority: str = "normal"


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    status: NotificationStatus
    created_at: datetime


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.get("/readiness")
async def readiness():
    return {"status": "ready", "service": "notification-service"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/notifications", response_model=NotificationResponse, status_code=201)
async def send_notification(request: SendNotificationRequest):
    """Queue a notification for delivery."""
    return NotificationResponse(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        type=request.type,
        status=NotificationStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )
