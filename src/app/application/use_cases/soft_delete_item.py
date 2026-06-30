from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.exceptions import ItemNotFoundError
from app.domain.exceptions.item import (
    ItemInUseInInventoryError,
    ItemUsedInActiveZoneError,
    ItemListedInShopError,
)


class SoftDeleteItemUseCase:
    def __init__(
        self,
        item_repo: ItemRepository,
        inventory_repo: InventoryRepository,
        zone_repo: ZoneRepository,
        shop_item_repo: ShopItemRepository,
    ):
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo
        self.zone_repo = zone_repo
        self.shop_item_repo = shop_item_repo

    async def execute(self, item_id: UUID, uow: UnitOfWork) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.is_deleted():
            raise ItemNotFoundError(item_id)

        inventory_count = await self.inventory_repo.count_by_item_id(item_id)
        if inventory_count > 0:
            raise ItemInUseInInventoryError(item.name, inventory_count)

        zone_count = await self.zone_repo.count_active_by_loot_item_id(item_id)
        if zone_count > 0:
            raise ItemUsedInActiveZoneError(item.name, zone_count)

        shop_items = await self.shop_item_repo.get_all_by_item_id(item_id)
        active_shop_items = [s for s in shop_items if s.is_active]
        if active_shop_items:
            raise ItemListedInShopError(item.name, len(active_shop_items))

        item.soft_delete()
        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
