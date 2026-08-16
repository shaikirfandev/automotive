"""Unit tests for Ledger Service."""
import pytest
from services.ledger_service.schemas import CreateLedgerEntryRequest
from services.ledger_service.service import LedgerServiceHandler


class TestLedgerService:
    """Test double-entry ledger operations."""

    @pytest.fixture
    def service(self):
        return LedgerServiceHandler()

    @pytest.mark.asyncio
    async def test_create_entry(self, service):
        request = CreateLedgerEntryRequest(
            transaction_reference="txn-001",
            debit_account_id="account-A",
            credit_account_id="account-B",
            amount=5000,
            currency="INR",
            description="Payment transfer",
            idempotency_key="idem-001",
        )
        result = await service.create_entry(request)
        assert result.amount == 5000
        assert result.debit_account_id == "account-A"
        assert result.credit_account_id == "account-B"
        assert result.debit_entry_id != result.credit_entry_id

    @pytest.mark.asyncio
    async def test_verify_integrity(self, service):
        is_valid = await service.verify_integrity()
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_get_balance(self, service):
        result = await service.get_balance("account-1")
        assert result.account_id == "account-1"
        assert result.net_balance == result.total_credits - result.total_debits

    def test_amount_must_be_positive(self):
        with pytest.raises(Exception):
            CreateLedgerEntryRequest(
                transaction_reference="txn-001",
                debit_account_id="a",
                credit_account_id="b",
                amount=0,
                idempotency_key="k",
            )
