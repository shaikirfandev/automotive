"""Unit tests for Wallet Service."""
import pytest
from services.wallet_service.schemas import (
    CreateWalletRequest,
    CreditRequest,
    DebitRequest,
    TransferRequest,
    WalletStatus,
    TransactionType,
)
from services.wallet_service.service import WalletServiceHandler


class TestWalletServiceHandler:
    """Test wallet operations."""

    @pytest.fixture
    def service(self):
        return WalletServiceHandler()

    @pytest.mark.asyncio
    async def test_create_wallet(self, service):
        request = CreateWalletRequest(user_id="user-1", currency="INR")
        result = await service.create_wallet(request)
        assert result.user_id == "user-1"
        assert result.balance == 0
        assert result.status == WalletStatus.ACTIVE
        assert result.version == 1
        assert result.currency == "INR"

    @pytest.mark.asyncio
    async def test_credit_wallet(self, service):
        request = CreditRequest(amount=5000, reference_id="ref-1", description="Top up")
        result = await service.credit("wallet-1", request)
        assert result.type == TransactionType.CREDIT
        assert result.amount == 5000
        assert result.reference_id == "ref-1"

    @pytest.mark.asyncio
    async def test_debit_wallet(self, service):
        request = DebitRequest(amount=3000, reference_id="ref-2", description="Payment")
        result = await service.debit("wallet-1", request)
        assert result.type == TransactionType.DEBIT
        assert result.amount == 3000

    @pytest.mark.asyncio
    async def test_transfer(self, service):
        request = TransferRequest(
            from_wallet_id="wallet-1",
            to_wallet_id="wallet-2",
            amount=1000,
            reference_id="ref-3",
        )
        result = await service.transfer(request)
        assert result.type == TransactionType.TRANSFER_OUT
        assert result.amount == 1000


class TestWalletRequestValidation:
    """Test wallet request schema validation."""

    def test_credit_amount_must_be_positive(self):
        with pytest.raises(Exception):
            CreditRequest(amount=0, reference_id="ref-1")

    def test_debit_amount_must_be_positive(self):
        with pytest.raises(Exception):
            DebitRequest(amount=-100, reference_id="ref-1")

    def test_transfer_amount_must_be_positive(self):
        with pytest.raises(Exception):
            TransferRequest(
                from_wallet_id="w1",
                to_wallet_id="w2",
                amount=0,
                reference_id="ref-1",
            )
