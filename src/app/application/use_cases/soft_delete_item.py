from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.exceptions import ItemNotFoundError, ItemInUseError


class SoftDeleteItemUseCase:
    def __init__(
        self,
        item_repo: ItemRepository,
        inventory_repo: InventoryRepository,
        zone_repo: ZoneRepository,
        loot_box_repo: LootBoxRepository,
        shop_item_repo: ShopItemRepository,
    ):
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo
        self.zone_repo = zone_repo
        self.loot_box_repo = loot_box_repo
        self.shop_item_repo = shop_item_repo

    async def execute(self, item_id: UUID, uow: UnitOfWork) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.is_deleted():
            raise ItemNotFoundError(item_id)

        details: list[str] = []

        inventory_count = await self.inventory_repo.count_by_item_id(item_id)
        if inventory_count > 0:
            details.append(f"{inventory_count} player inventories")

        zones = await self.zone_repo.get_all()
        for zone in zones:
            if zone.loot_table:
                for entry in zone.loot_table:
                    if entry.get("item_id") == str(item_id):
                        details.append(f"loot table of zone '{zone.name}'")
                        break

        loot_boxes = await self.loot_box_repo.get_all()
        for lb in loot_boxes:
            if lb.entries:
                for entry in lb.entries:
                    if entry.item_id == item_id:
                        details.append(f"loot box '{lb.name}'")
                        break

        shop_items = await self.shop_item_repo.get_all_by_item_id(item_id)
        if shop_items:
            active_count = sum(1 for si in shop_items if si.is_active)
            if active_count > 0:
                details.append(f"{active_count} active shop items")

        if details:
            raise ItemInUseError(item.name, details)

        item.soft_delete()
        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
