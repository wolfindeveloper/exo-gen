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
    ItemUsedInLootBoxError,
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

        usage = await self.item_repo.check_usage(item_id)

        if usage.inventory_count > 0:
            raise ItemInUseInInventoryError(item.name, usage.inventory_count)

        if usage.zone_names:
            raise ItemUsedInActiveZoneError(item.name, len(usage.zone_names))

        if usage.loot_box_names:
            raise ItemUsedInLootBoxError(item.name, len(usage.loot_box_names))

        if usage.active_shop_items > 0:
            raise ItemListedInShopError(item.name, usage.active_shop_items)

        item.soft_delete()
        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
