from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.inventory import Inventory

class InventoryRepository(ABC):
    @abstractmethod
    async def get_by_player_id(self, player_id: UUID, for_update: bool = False) -> Inventory:
        """Загружает весь инвентарь игрока. Если инвентарь пуст, возвращает пустой Агрегат."""
        pass

    @abstractmethod
    async def count_by_item_id(self, item_id: UUID) -> int:
        """Возвращает общее количество предметов с данным item_id во всех инвентарях"""
        pass

    @abstractmethod
    async def save(self, inventory: Inventory) -> None:
        """Синхронизирует состояние Агрегата с базой данных (добавляет новые, обновляет количество, удаляет пустые)."""
        pass