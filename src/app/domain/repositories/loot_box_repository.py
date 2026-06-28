from abc import ABC, abstractmethod

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.value_objects.loot_box import LootBoxType


class LootBoxRepository(ABC):
    @abstractmethod
    async def get_by_type(self, box_type: LootBoxType) -> LootBoxConfig | None:
        pass

    @abstractmethod
    async def save(self, config: LootBoxConfig) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[LootBoxConfig]:
        pass
