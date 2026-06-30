from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.zone import Zone


class ZoneRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Zone]:
        pass

    @abstractmethod
    async def get_by_id(self, zone_id: UUID) -> Zone | None:
        pass
        

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Zone], int]:
        pass

    @abstractmethod
    async def count_active_by_loot_item_id(self, item_id: UUID) -> int:
        """Возвращает количество активных зон, в loot_table которых есть указанный item_id"""
        pass

    @abstractmethod
    async def save(self, zone: Zone) -> None:
        pass