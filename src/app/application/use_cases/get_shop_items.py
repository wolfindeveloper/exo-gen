from app.application.dtos.shop_dto import ShopItemResponseDTO
from app.domain.repositories.shop_repository import ShopItemRepository


class GetShopItemsUseCase:
    def __init__(self, shop_item_repo: ShopItemRepository):
        self.shop_item_repo = shop_item_repo

    async def execute(self) -> list[ShopItemResponseDTO]:
        items = await self.shop_item_repo.get_all_active()
        return [ShopItemResponseDTO(
            id=item.id,
            item_id=item.item_id,
            price_xgen=item.price_xgen,
            daily_limit=item.daily_limit,
            stock_limit=item.stock_limit,
            is_active=item.is_active,
        ) for item in items]
