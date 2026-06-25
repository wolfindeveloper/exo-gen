from uuid import UUID
from app.domain.entities.player import Player
from app.domain.entities.item import ItemType
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

    async def execute(self, player: Player, dto: UseItemDTO) -> UseItemResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)
        if not ship:
            raise ValueError("Ship not found or does not belong to player")

        # 2. Достаем предмет из справочника
        item = await self.item_repo.get_by_id(dto.item_id)
        if not item:
            raise ValueError("Item does not exist in catalog")

        # 3. Проверяем, что предмет вообще можно использовать (это расходник)
        if item.type != ItemType.CONSUMABLE:
            raise ValueError("This item cannot be used directly")

        # 4. Проверяем, есть ли он в инвентаре игрока
        inventory = await self.inventory_repo.get_by_player_id(player.id)
        if not inventory.has_item(item.id):
            raise ValueError("You don't have this item in your inventory")

        # 5. Применяем эффекты из JSONB словаря (effect)
        if "restore_tea" in item.effect:
            ship.restore_tea(item.effect["restore_tea"])
            
        if "restore_optimism" in item.effect:
            ship.restore_optimism(item.effect["restore_optimism"])

        # 6. Списываем одну штуку из инвентаря (доменный метод сам удалит запись, если quantity станет 0)
        inventory.remove_item(item.id, quantity=1)

        # 7. Сохраняем изменения
        await self.player_repo.save(player)
        await self.inventory_repo.save(inventory)

        return UseItemResponseDTO(
            message=f"Successfully used {item.name} on {ship.name}!",
            new_tea_level=ship.tea_level,
            new_optimism=ship.optimism
        )