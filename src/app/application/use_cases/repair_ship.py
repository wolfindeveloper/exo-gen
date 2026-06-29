from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.inventory import NoSuitableConsumableError
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.services.consumable_selector import ConsumableSelector
from app.application.dtos.ship_service_dto import RepairShipDTO, RepairShipResponseDTO


class RepairShipUseCase:
    """Выбирает оптимальный consumable с эффектом restore_optimism в инвентаре и применяет его к кораблю."""

    EFFECT_KEY = "restore_optimism"

    def __init__(
        self,
        player_repo: PlayerRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
    ):
        self.player_repo = player_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo
        self.selector = ConsumableSelector()

    async def execute(
        self, player: Player, dto: RepairShipDTO, uow: UnitOfWork
    ) -> RepairShipResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)
        if not ship:
            raise ShipNotFoundError("Ship not found or does not belong to player")

        inventory = await self.inventory_repo.get_by_player_id(player.id)

        candidate_items = await self.item_repo.get_consumables_with_effect(self.EFFECT_KEY)
        if not candidate_items:
            raise NoSuitableConsumableError(self.EFFECT_KEY)

        available_items = [
            (item, inv_item.quantity)
            for item in candidate_items
            if (inv_item := next((i for i in inventory.items if i.item_id == item.id), None))
            and inv_item.quantity > 0
        ]

        decision = self.selector.select_for_repair(
            available_items=available_items,
            current_optimism=ship.optimism.value,
        )

        if decision.chosen_item is None:
            raise NoSuitableConsumableError(self.EFFECT_KEY)

        chosen_item = decision.chosen_item
        optimism_restored = float(chosen_item.effect[self.EFFECT_KEY])
        ship.restore_optimism(optimism_restored)

        inventory.remove_item(chosen_item.id, quantity=1)

        uow.track(player)
        await self.player_repo.save(player)
        await self.inventory_repo.save(inventory)
        await uow.commit()

        return RepairShipResponseDTO(
            message=f"Repaired {ship.name} with {chosen_item.name}",
            item_used_id=chosen_item.id,
            item_used_name=chosen_item.name,
            optimism_restored=optimism_restored,
            new_optimism_level=ship.optimism.value,
        )
