from uuid import UUID

from app.domain.exceptions.base import DomainError


class LootBoxConfigNotFoundError(DomainError):
    def __init__(self, config_id: str):
        super().__init__(f"LootBoxConfig {config_id} not found")
