from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID
from typing import Any

from app.domain.entities.shop import ShopItem, PurchaseHistory, ShopCategory


class ShopCategoryRepository(ABC):
    @abstractmethod
    async def get_all_active(self) -> list[ShopCategory]:
        """Возвращает активные категории, отсортированные по sort_order"""
        pass

    @abstractmethod
    async def get_all(self) -> list[ShopCategory]:
        """Возвращает все категории (кроме soft-deleted), включая неактивные"""
        pass

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> ShopCategory | None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> ShopCategory | None:
        pass

    @abstractmethod
    async def count_items_by_category(self, category_id: UUID) -> int:
        """Возвращает количество не удалённых товаров в указанной категории"""
        pass

    @abstractmethod
    async def save(self, category: ShopCategory) -> None:
        pass


class ShopItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, shop_item_id: UUID) -> ShopItem | None:
        pass

    @abstractmethod
    async def get_by_id_for_update(self, shop_item_id: UUID) -> ShopItem | None:
        """Загружает товар с блокировкой строки (SELECT ... FOR UPDATE)"""
        pass

    @abstractmethod
    async def get_all_active(self) -> list[ShopItem]:
        pass

    @abstractmethod
    async def get_all(self) -> list[ShopItem]:
        """Возвращает все товары в магазине (кроме soft-deleted)"""
        pass

    @abstractmethod
    async def get_all_by_item_id(self, item_id: UUID) -> list[ShopItem]:
        """Возвращает все shop_items, ссылающиеся на указанный item_id"""
        pass

    @abstractmethod
    async def save(self, shop_item: ShopItem) -> None:
        pass

    @abstractmethod
    async def add(self, data: dict) -> Any:
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
