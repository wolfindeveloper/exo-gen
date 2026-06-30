from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ShopItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    item_id: UUID
    price_xgen: int
    daily_limit: int
    stock_limit: int
    is_active: bool


class ShopItemAnalyticsDTO(BaseModel):
    total_purchases: int
    today_purchases: int
    revenue_xgen: int


class ShopItemWithAnalyticsDTO(BaseModel):
    id: UUID
    item_id: UUID
    price_xgen: int
    daily_limit: int
    stock_limit: int
    is_active: bool
    analytics: ShopItemAnalyticsDTO


class PurchaseItemDTO(BaseModel):
    shop_item_id: UUID


class PurchaseItemResponseDTO(BaseModel):
    success: bool
    message: str
    item_id: UUID | None = None
    quantity: int = 1
    xgen_spent: int = 0
