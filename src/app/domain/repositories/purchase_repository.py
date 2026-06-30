from abc import ABC, abstractmethod
from uuid import UUID


class PurchaseRepository(ABC):
    @abstractmethod
    async def count_by_shop_item(self, shop_item_id: UUID) -> int:
        """Возвращает общее количество покупок товара"""
        pass

    @abstractmethod
    async def count_by_shop_item_today(self, shop_item_id: UUID) -> int:
        """Возвращает количество покупок товара за сегодня"""
        pass

    @abstractmethod
    async def sum_xgen_by_shop_item(self, shop_item_id: UUID) -> int:
        """Возвращает суммарную выручку в xgen по товару"""
        pass

    @abstractmethod
    async def add(self, player_id: UUID, shop_item_id: UUID, xgen_spent: int) -> None:
        """Добавляет запись о покупке"""
        pass
