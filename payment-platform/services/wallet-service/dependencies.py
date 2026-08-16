"""Wallet service dependency injection."""
from services.wallet_service.service import WalletServiceHandler


async def get_wallet_service() -> WalletServiceHandler:
    """Provide WalletServiceHandler instance."""
    return WalletServiceHandler()
