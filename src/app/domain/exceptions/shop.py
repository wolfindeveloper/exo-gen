from uuid import UUID

from app.domain.exceptions.base import DomainError


class ShopItemNotFoundError(DomainError):
    def __init__(self, shop_item_id: UUID):
        self.shop_item_id = shop_item_id
        super().__init__(f"Shop item {shop_item_id} not found")


class ShopItemDailyLimitReachedError(DomainError):
    def __init__(self, shop_item_id: UUID):
        self.shop_item_id = shop_item_id
        super().__init__(f"Daily purchase limit reached for shop item {shop_item_id}")


class ShopItemOutOfStockError(DomainError):
    def __init__(self, shop_item_id: UUID):
        self.shop_item_id = shop_item_id
        super().__init__(f"Shop item {shop_item_id} is out of stock")
