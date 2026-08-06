from uuid import UUID
from dataclasses import dataclass

from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
from app.domain.uow import UnitOfWork
from app.domain.services.loot_box_service import LootBoxService
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository


@dataclass
class OpenLootBoxResult:
    xgen_earned: int
    fragments_earned: int
    items_earned: list[dict]


class OpenLootBoxUseCase:
    def __init__(
        self,
        loot_box_service: LootBoxService,
        loot_box_repo: LootBoxRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
    ):
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(
        self,
        player: Player,
        box_type: str,
        uow: UnitOfWork,
        inventory_item_id: UUID | None = None,
    ) -> OpenLootBoxResult:
        if inventory_item_id is not None:
            inventory = await self.inventory_repo.get_by_player_id(player.id, for_update=True)
            inventory.remove_item(inventory_item_id, quantity=1)
            await self.inventory_repo.save(inventory)

        config = await self.loot_box_repo.get_by_type(box_type)
        if not config or not config.is_active:
            return OpenLootBoxResult(0, 0, [])

        loot = self.loot_box_service.generate(config)

        player.add_xgen(loot.xgen)
        player.add_fragments(loot.fragments)

        item_ids = [UUID(d["item_id"]) for d in loot.items]
        items = await self.item_repo.get_by_ids(item_ids)
        item_type_map = {item.id: item.type for item in items}
        item_name_map = {item.id: item.name for item in items}
        item_image_map = {item.id: item.image_url for item in items}

        items_earned = []
        for item_drop in loot.items:
            item_id = UUID(item_drop["item_id"])
            amount = item_drop["amount"]
            await self.inventory_repo.add_item_quantity(player.id, item_id, amount)
            if item_type_map.get(item_id) == ItemType.ARTIFACT:
                player.increment_artifacts_found(amount)
            items_earned.append({
                "item_id": item_id,
                "amount": amount,
                "name": item_name_map.get(item_id),
                "image_url": item_image_map.get(item_id),
            })

        uow.track(player)

        return OpenLootBoxResult(
            xgen_earned=loot.xgen,
            fragments_earned=loot.fragments,
            items_earned=items_earned,
        )
