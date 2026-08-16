"""Unit tests for Payment Service.

Tests business logic without external dependencies.
Uses pytest-asyncio for async test support.
"""
import pytest
from datetime import datetime, timezone

from services.payment_service.schemas import (
    CreatePaymentRequest,
    PaymentStatus,
    PaymentMethod,
)
from services.payment_service.service import (
    PaymentServiceHandler,
    validate_transition,
    VALID_TRANSITIONS,
)


class TestPaymentStateTransitions:
    """Test payment state machine."""

    def test_created_to_pending_valid(self):
        assert validate_transition(PaymentStatus.CREATED, PaymentStatus.PENDING) is True

    def test_created_to_success_invalid(self):
        assert validate_transition(PaymentStatus.CREATED, PaymentStatus.SUCCESS) is False

    def test_pending_to_processing_valid(self):
        assert validate_transition(PaymentStatus.PENDING, PaymentStatus.PROCESSING) is True

    def test_processing_to_success_valid(self):
        assert validate_transition(PaymentStatus.PROCESSING, PaymentStatus.SUCCESS) is True

    def test_processing_to_failed_valid(self):
        assert validate_transition(PaymentStatus.PROCESSING, PaymentStatus.FAILED) is True

    def test_success_to_refunded_valid(self):
        assert validate_transition(PaymentStatus.SUCCESS, PaymentStatus.REFUNDED) is True

    def test_refunded_is_terminal(self):
        """Refunded is a terminal state - no transitions allowed."""
        for status in PaymentStatus:
            assert validate_transition(PaymentStatus.REFUNDED, status) is False

    def test_reversed_is_terminal(self):
        """Reversed is a terminal state."""
        for status in PaymentStatus:
            assert validate_transition(PaymentStatus.REVERSED, status) is False

    def test_all_states_have_transitions_defined(self):
        """Every state must have transitions defined (even if empty)."""
        for status in PaymentStatus:
            assert status in VALID_TRANSITIONS


class TestCreatePaymentRequest:
    """Test payment request validation."""

    def test_valid_payment_request(self):
        request = CreatePaymentRequest(
            payer_id="user-1",
            payee_id="user-2",
            amount=1000,
            currency="INR",
            payment_method=PaymentMethod.WALLET,
        )
        assert request.amount == 1000
        assert request.currency == "INR"

    def test_negative_amount_rejected(self):
        with pytest.raises(Exception):
            CreatePaymentRequest(
                payer_id="user-1",
                payee_id="user-2",
                amount=-100,
            )

    def test_zero_amount_rejected(self):
        with pytest.raises(Exception):
            CreatePaymentRequest(
                payer_id="user-1",
                payee_id="user-2",
                amount=0,
            )

    def test_excessive_amount_rejected(self):
        with pytest.raises(Exception):
            CreatePaymentRequest(
                payer_id="user-1",
                payee_id="user-2",
                amount=2000000_00,  # Exceeds max
            )

    def test_invalid_currency_format(self):
        with pytest.raises(Exception):
            CreatePaymentRequest(
                payer_id="user-1",
                payee_id="user-2",
                amount=1000,
                currency="invalid",
            )


class TestPaymentServiceHandler:
    """Test payment service business logic."""

    @pytest.fixture
    def service(self):
        return PaymentServiceHandler()

    @pytest.mark.asyncio
    async def test_create_payment_returns_created_status(self, service):
        request = CreatePaymentRequest(
            payer_id="user-1",
            payee_id="user-2",
            amount=5000,
            currency="INR",
            payment_method=PaymentMethod.WALLET,
        )
        result = await service.create_payment(
            request=request,
            idempotency_key="test-key-123",
            request_id="req-456",
        )
        assert result.status == PaymentStatus.CREATED
        assert result.amount == 5000
        assert result.payer_id == "user-1"
        assert result.payee_id == "user-2"
        assert result.idempotency_key == "test-key-123"

    @pytest.mark.asyncio
    async def test_create_payment_generates_uuid(self, service):
        request = CreatePaymentRequest(
            payer_id="user-1",
            payee_id="user-2",
            amount=1000,
        )
        result = await service.create_payment(
            request=request,
            idempotency_key="key-1",
            request_id="req-1",
        )
        assert len(result.id) == 36  # UUID format

    @pytest.mark.asyncio
    async def test_get_payment_not_found(self, service):
        result = await service.get_payment("nonexistent-id")
        assert result is None
