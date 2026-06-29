from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.entities.base import AggregateRoot
from app.domain.exceptions.shop import (
    ShopItemDailyLimitReachedError,
    ShopItemOutOfStockError,
)


@dataclass
class ShopItem(AggregateRoot):
    id: UUID
    item_id: UUID
    price_xgen: int
    daily_limit: int = 0
    stock_limit: int = 0
    is_active: bool = True

    def can_purchase(self, purchase_count_today: int, total_purchase_count: int) -> None:
        if not self.is_active:
            raise ShopItemDailyLimitReachedError(self.id)

        if self.daily_limit > 0 and purchase_count_today >= self.daily_limit:
            raise ShopItemDailyLimitReachedError(self.id)

        if self.stock_limit > 0 and total_purchase_count >= self.stock_limit:
            raise ShopItemOutOfStockError(self.id)


@dataclass
class PurchaseHistory:
    id: UUID
    player_id: UUID
    shop_item_id: UUID
    purchased_at: datetime
