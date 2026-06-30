from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.domain.entities.shop import ShopItem, PurchaseHistory


class ShopItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, shop_item_id: UUID) -> ShopItem | None:
        pass

    @abstractmethod
    async def get_all_active(self) -> list[ShopItem]:
        pass

    @abstractmethod
    async def get_all_by_item_id(self, item_id: UUID) -> list[ShopItem]:
        """Возвращает все shop_items, ссылающиеся на указанный item_id"""
        pass

    @abstractmethod
    async def save(self, shop_item: ShopItem) -> None:
        pass


class PurchaseHistoryRepository(ABC):
    @abstractmethod
    async def get_by_player_and_shop_item(self, player_id: UUID, shop_item_id: UUID) -> list[PurchaseHistory]:
        pass

    @abstractmethod
    async def get_purchase_count_today(self, player_id: UUID, shop_item_id: UUID, day: date) -> int:
        """Возвращает количество покупок данного товара игроком за указанный день"""
        pass

    @abstractmethod
    async def get_total_purchase_count(self, shop_item_id: UUID) -> int:
        """Возвращает общее количество покупок данного товара (для stock_limit)"""
        pass

    @abstractmethod
    async def save(self, history: PurchaseHistory) -> None:
        pass
