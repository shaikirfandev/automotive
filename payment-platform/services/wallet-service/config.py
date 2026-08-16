"""Wallet service configuration."""
from shared.config import BaseServiceSettings


class WalletServiceSettings(BaseServiceSettings):
    service_name: str = "wallet-service"
    port: int = 8004
    max_wallet_balance: int = 10000000_00  # in cents
    max_single_transaction: int = 1000000_00


settings = WalletServiceSettings()
