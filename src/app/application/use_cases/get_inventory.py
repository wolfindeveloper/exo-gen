from app.domain.entities.player import Player
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.application.dtos.inventory_dto import InventoryResponseDTO, InventoryItemDTO
from app.application.dtos.item_dto import ItemResponseDTO

class GetInventoryUseCase:
    def __init__(
        self, 
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository
    ):
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(self, player: Player) -> InventoryResponseDTO:
        # 1. Загружаем рюкзак игрока
        inventory = await self.inventory_repo.get_by_player_id(player.id)

        # 2. Загружаем предметы, которые есть в инвентаре (через get_by_ids — без фильтра deleted_at)
        item_ids = [inv_item.item_id for inv_item in inventory.items]
        if item_ids:
            all_items = await self.item_repo.get_by_ids(item_ids)
            items_dict = {item.id: item for item in all_items}
        else:
            items_dict = {}

        # 3. Склеиваем
        inventory_dtos = []
        for inv_item in inventory.items:
            item_domain = items_dict.get(inv_item.item_id)
            if item_domain:
                # Превращаем доменный Item в DTO
                item_dto = ItemResponseDTO(
                    id=item_domain.id,
                    name=item_domain.name,
                    description=item_domain.description,
                    type=item_domain.type,
                    rarity=item_domain.rarity,
                    effect=item_domain.effect,
                    is_tradable=item_domain.is_tradable,
                    sell_price=item_domain.sell_price,
                    image_url=item_domain.image_url or "",
                )
                inventory_dtos.append(InventoryItemDTO(
                    item=item_dto,
                    quantity=inv_item.quantity
                ))

        return InventoryResponseDTO(items=inventory_dtos)