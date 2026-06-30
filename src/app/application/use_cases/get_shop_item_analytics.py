from uuid import UUID

from app.domain.repositories.purchase_repository import PurchaseRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.exceptions.shop import ShopItemNotFoundError


class ShopItemAnalyticsResult:
    def __init__(self, total_purchases: int, today_purchases: int, revenue_xgen: int):
        self.total_purchases = total_purchases
        self.today_purchases = today_purchases
        self.revenue_xgen = revenue_xgen


class GetShopItemAnalyticsUseCase:
    def __init__(
        self,
        shop_item_repo: ShopItemRepository,
        purchase_repo: PurchaseRepository,
    ):
        self.shop_item_repo = shop_item_repo
        self.purchase_repo = purchase_repo

    async def execute(self, shop_item_id: UUID) -> ShopItemAnalyticsResult:
        shop_item = await self.shop_item_repo.get_by_id(shop_item_id)
        if not shop_item:
            raise ShopItemNotFoundError(f"Shop item {shop_item_id} not found")

        total_purchases = await self.purchase_repo.count_by_shop_item(shop_item_id)
        today_purchases = await self.purchase_repo.count_by_shop_item_today(shop_item_id)
        revenue_xgen = await self.purchase_repo.sum_xgen_by_shop_item(shop_item_id)

        return ShopItemAnalyticsResult(
            total_purchases=total_purchases,
            today_purchases=today_purchases,
            revenue_xgen=revenue_xgen,
        )
