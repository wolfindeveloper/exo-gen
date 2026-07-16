from fastapi import APIRouter, Depends, HTTPException
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.application.use_cases.get_inventory import GetInventoryUseCase
from app.application.use_cases.get_items import GetItemsUseCase
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase
from app.application.dtos.inventory_dto import InventoryResponseDTO
from app.application.dtos.item_dto import ItemResponseDTO
from app.application.dtos.inventory_dto import UseItemDTO, UseItemResponseDTO
from app.application.dtos.inventory_dto import OpenBoxRequestDTO, OpenBoxResponseDTO
from app.application.dtos.claim_expedition_dto import ClaimedItemDTO
from app.application.use_cases.use_item import UseItemUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.domain.services.loot_box_service import LootBoxService
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_player_repo, get_inventory_repo, get_item_repo, get_loot_box_repo, get_uow

router = APIRouter(tags=["Inventory"])

@router.get("/items", response_model=list[ItemResponseDTO])
async def get_all_items(
    item_repo: ItemRepository = Depends(get_item_repo)
):
    """Возвращает глобальный справочник всех предметов в игре"""
    use_case = GetItemsUseCase(item_repo)
    return await use_case.execute()

@router.get("/inventory", response_model=InventoryResponseDTO)
async def get_inventory(
    current_player: Player = Depends(get_current_player),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo)
):
    """Возвращает рюкзак конкретного игрока"""
    use_case = GetInventoryUseCase(inventory_repo, item_repo)
    try:
        return await use_case.execute(current_player)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/use", response_model=UseItemResponseDTO)
async def use_item(
    dto: UseItemDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = UseItemUseCase(player_repo, inventory_repo, item_repo)
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/inventory/open-box", response_model=OpenBoxResponseDTO)
async def open_loot_box(
    dto: OpenBoxRequestDTO,
    current_player: Player = Depends(get_current_player),
    uow: UnitOfWork = Depends(get_uow),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
):
    async with uow:
        if dto.inventory_item_id:
            inventory = await inventory_repo.get_by_player_id(
                current_player.id, for_update=True
            )
            try:
                inventory.remove_item(dto.inventory_item_id, quantity=1)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Коробка не найдена: {e}")
            await inventory_repo.save(inventory)

        use_case = OpenLootBoxUseCase(
            LootBoxService(), loot_box_repo, inventory_repo, item_repo
        )
        result = await use_case.execute(current_player, dto.box_type, uow)

        return OpenBoxResponseDTO(
            xgen_earned=result.xgen_earned,
            fragments_earned=result.fragments_earned,
            items_earned=[
                ClaimedItemDTO(
                    item_id=item["item_id"],
                    amount=item["amount"],
                )
                for item in result.items_earned
            ],
        )