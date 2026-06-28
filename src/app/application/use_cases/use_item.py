from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
from app.domain.uow import UnitOfWork
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.inventory import ItemNotFoundError, ItemNotConsumableError, ItemNotInInventoryError
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.application.dtos.inventory_dto import UseItemDTO, UseItemResponseDTO


class UseItemUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository
    ):
        self.player_repo = player_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(self, player: Player, dto: UseItemDTO, uow: UnitOfWork) -> UseItemResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)
        if not ship:
            raise ShipNotFoundError("Ship not found or does not belong to player")

        item = await self.item_repo.get_by_id(dto.item_id)
        if not item:
            raise ItemNotFoundError(dto.item_id)

        if item.type != ItemType.CONSUMABLE:
            raise ItemNotConsumableError("This item cannot be used directly")

        inventory = await self.inventory_repo.get_by_player_id(player.id)
        if not inventory.has_item(item.id):
            raise ItemNotInInventoryError(item.id)

        if "restore_tea" in item.effect:
            ship.restore_tea(item.effect["restore_tea"])

        if "restore_optimism" in item.effect:
            ship.restore_optimism(item.effect["restore_optimism"])

        inventory.remove_item(item.id, quantity=1)

        await self.player_repo.save(player)
        await self.inventory_repo.save(inventory)
        await uow.commit()

        return UseItemResponseDTO(
            message=f"Successfully used {item.name} on {ship.name}!",
            new_tea_level=ship.tea_level.value,
            new_optimism=ship.optimism.value
        )
