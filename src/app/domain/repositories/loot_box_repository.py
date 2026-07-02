from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.loot_box_config import LootBoxConfig


class LootBoxRepository(ABC):
    @abstractmethod
    async def get_by_id(self, config_id: UUID) -> LootBoxConfig | None:
        pass

    @abstractmethod
    async def get_by_type(self, box_type: str) -> LootBoxConfig | None:
        pass

    @abstractmethod
    async def save(self, config: LootBoxConfig) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[LootBoxConfig]:
        pass
