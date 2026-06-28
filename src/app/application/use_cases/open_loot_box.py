from uuid import UUID
from dataclasses import dataclass

from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.services.loot_box_service import LootBoxService
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.inventory_repository import InventoryRepository


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
    ):
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo

    async def execute(
        self,
        player: Player,
        box_type: LootBoxType,
        uow: UnitOfWork,
    ) -> OpenLootBoxResult:
        config = await self.loot_box_repo.get_by_type(box_type)
        if not config or not config.is_active:
            return OpenLootBoxResult(0, 0, [])

        loot = self.loot_box_service.generate(config)

        player.add_xgen(loot.xgen)
        player.add_fragments(loot.fragments)

        inventory = await self.inventory_repo.get_by_player_id(player.id)
        items_earned = []
        for item_drop in loot.items:
            item_id = UUID(item_drop["item_id"])
            amount = item_drop["amount"]
            inventory.add_item(item_id=item_id, quantity=amount)
            items_earned.append({"item_id": item_id, "amount": amount})

        await self.inventory_repo.save(inventory)

        return OpenLootBoxResult(
            xgen_earned=loot.xgen,
            fragments_earned=loot.fragments,
            items_earned=items_earned,
        )
