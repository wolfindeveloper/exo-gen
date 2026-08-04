from uuid import UUID

from app.application.dtos.shop_dto import ShopItemResponseDTO, ShopItemInfoDTO, BundleItemInfoDTO
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.repositories.item_repository import ItemRepository


class GetShopItemsUseCase:
    def __init__(self, shop_item_repo: ShopItemRepository, item_repo: ItemRepository):
        self.shop_item_repo = shop_item_repo
        self.item_repo = item_repo

    async def execute(self) -> list[ShopItemResponseDTO]:
        items = await self.shop_item_repo.get_all_active()

        item_ids: list[UUID] = []
        for shop_item in items:
            if shop_item.item_id:
                item_ids.append(shop_item.item_id)
            for bundle_entry in (shop_item.bundle_items or []):
                bid = bundle_entry.get("item_id")
                if bid:
                    try:
                        uid = UUID(bid) if isinstance(bid, str) else bid
                        if uid not in item_ids:
                            item_ids.append(uid)
                    except (ValueError, AttributeError):
                        pass

        items_catalog = await self.item_repo.get_by_ids(item_ids) if item_ids else []
        items_map = {str(it.id): it for it in items_catalog}

        result = []
        for shop_item in items:
            item_info = None
            if shop_item.item_id:
                catalog_item = items_map.get(str(shop_item.item_id))
                if catalog_item:
                    item_info = ShopItemInfoDTO(
                        id=catalog_item.id,
                        name=catalog_item.name,
                        description=catalog_item.description,
                        type=catalog_item.type.value,
                        rarity=catalog_item.rarity,
                        effect=catalog_item.effect,
                        image_url=catalog_item.image_url or "",
                    )

            bundle_items_info = []
            for bundle_entry in (shop_item.bundle_items or []):
                bid = bundle_entry.get("item_id")
                qty = bundle_entry.get("quantity", 1)
                if bid:
                    bundle_item = items_map.get(str(bid))
                    if bundle_item:
                        bundle_items_info.append(BundleItemInfoDTO(
                            item_id=bundle_item.id,
                            name=bundle_item.name,
                            description=bundle_item.description,
                            image_url=bundle_item.image_url or "",
                            quantity=qty,
                        ))

            result.append(ShopItemResponseDTO(
                id=shop_item.id,
                item_id=shop_item.item_id,
                price_xgen=shop_item.price_xgen,
                daily_limit=shop_item.daily_limit,
                stock_limit=shop_item.stock_limit,
                is_active=shop_item.is_active,
                bundle_items=shop_item.bundle_items or [],
                item_info=item_info,
                bundle_items_info=bundle_items_info,
            ))

        return result
