from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.item import Item

class ItemRepository(ABC):
    @abstractmethod
    async def save(self, item: Item) -> None:
        """Сохраняет новый предмет или обновляет существующий"""
        pass

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Item | None:
        """Ищет предмет по его ID"""
        pass

    @abstractmethod
    async def get_all(self) -> list[Item]:
        """Возвращает все предметы (для админки или магазина)"""
        pass

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Item], int]:
        pass

    @abstractmethod
    async def get_by_ids(self, item_ids: list[UUID]) -> list[Item]:
        """Возвращает предметы по списку их ID"""
        pass

    @abstractmethod
    async def get_consumables_with_effect(self, effect_key: str) -> list[Item]:
        """Возвращает все consumable предметы, имеющие указанный ключ в effect"""
        pass