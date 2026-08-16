"""Ledger service dependency injection."""
from services.ledger_service.service import LedgerServiceHandler


async def get_ledger_service() -> LedgerServiceHandler:
    return LedgerServiceHandler()
