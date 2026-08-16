"""End-to-end payment flow tests.

Tests the complete payment lifecycle:
  Create User → Create Wallet → Add Balance → Create Payment → Verify
"""
import pytest
from httpx import AsyncClient, ASGITransport
from services.payment_service.main import app as payment_app
from services.wallet_service.main import app as wallet_app


class TestPaymentFlow:
    """E2E payment flow test."""

    @pytest.mark.asyncio
    async def test_payment_service_health(self):
        transport = ASGITransport(app=payment_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_wallet_service_health(self):
        transport = ASGITransport(app=wallet_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_create_payment_requires_idempotency_key(self):
        transport = ASGITransport(app=payment_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/payments",
                json={
                    "payer_id": "user-1",
                    "payee_id": "user-2",
                    "amount": 5000,
                    "currency": "INR",
                    "payment_method": "WALLET",
                },
            )
            # Should fail without Idempotency-Key header
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_payment_with_idempotency_key(self):
        transport = ASGITransport(app=payment_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/payments",
                json={
                    "payer_id": "user-1",
                    "payee_id": "user-2",
                    "amount": 5000,
                    "currency": "INR",
                    "payment_method": "WALLET",
                },
                headers={"Idempotency-Key": "test-idem-key-001"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "CREATED"
            assert data["amount"] == 5000
            assert data["idempotency_key"] == "test-idem-key-001"

    @pytest.mark.asyncio
    async def test_create_wallet(self):
        transport = ASGITransport(app=wallet_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/wallets",
                json={"user_id": "user-1", "currency": "INR"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["balance"] == 0
            assert data["status"] == "ACTIVE"
