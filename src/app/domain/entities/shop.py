from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.base import AggregateRoot
from app.domain.exceptions.shop import (
    ShopItemDailyLimitReachedError,
    ShopItemOutOfStockError,
)


@dataclass
class ShopItem(AggregateRoot):
    id: UUID
    price_xgen: int
    item_id: UUID | None = None
    daily_limit: int = 0
    stock_limit: int = 0
    is_active: bool = True
    bundle_items: list[dict] = field(default_factory=list)
    deleted_at: datetime | None = None

    def update(
        self,
        price_xgen: int | None = None,
        daily_limit: int | None = None,
        stock_limit: int | None = None,
        is_active: bool | None = None,
        **kwargs: object,
    ) -> None:
        if "item_id" in kwargs:
            raise ValueError("Cannot change item_id directly")
        if price_xgen is not None:
            self.price_xgen = price_xgen
        if daily_limit is not None:
            self.daily_limit = daily_limit
        if stock_limit is not None:
            self.stock_limit = stock_limit
        if is_active is not None:
            self.is_active = is_active

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

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
