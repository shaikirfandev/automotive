"""Ledger service configuration."""
from shared.config import BaseServiceSettings


class LedgerServiceSettings(BaseServiceSettings):
    service_name: str = "ledger-service"
    port: int = 8007


settings = LedgerServiceSettings()
