from fastapi import APIRouter, Depends, HTTPException
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.application.use_cases.get_inventory import GetInventoryUseCase
from app.application.use_cases.get_items import GetItemsUseCase
from app.application.dtos.inventory_dto import InventoryResponseDTO
from app.application.dtos.item_dto import ItemResponseDTO
from app.application.dtos.inventory_dto import UseItemDTO, UseItemResponseDTO
from app.application.use_cases.use_item import UseItemUseCase
from app.domain.entities.player import Player
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_player_repo, get_inventory_repo, get_item_repo

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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/use", response_model=UseItemResponseDTO)
async def use_item(
    dto: UseItemDTO,
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo)
):
    use_case = UseItemUseCase(player_repo, inventory_repo, item_repo)
    try:
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))