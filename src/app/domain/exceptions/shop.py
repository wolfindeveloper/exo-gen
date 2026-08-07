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


class ShopCategoryNotFoundError(DomainError):
    def __init__(self, category_id: UUID):
        self.category_id = category_id
        super().__init__(f"Shop category {category_id} not found")


class ShopCategorySlugTakenError(DomainError):
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Shop category with slug '{slug}' already exists")


class ShopCategoryHasItemsError(DomainError):
    def __init__(self, category_id: UUID):
        self.category_id = category_id
        super().__init__(f"Cannot delete shop category {category_id}: it has linked items")
