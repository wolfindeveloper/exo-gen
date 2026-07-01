from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.security.rate_limiter import limiter
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.application.use_cases.refuel_ship import RefuelShipUseCase
from app.application.use_cases.repair_ship import RepairShipUseCase
from app.application.dtos.ship_service_dto import (
    RefuelShipDTO,
    RefuelShipResponseDTO,
    RepairShipDTO,
    RepairShipResponseDTO,
    ShipResponseDTO,
)
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import (
    get_player_repo,
    get_inventory_repo,
    get_item_repo,
    get_uow,
)

router = APIRouter(prefix="/ships", tags=["Ships"])


@router.get("/me", response_model=ShipResponseDTO)
@limiter.limit("60/minute")
async def get_my_ship(
    request: Request,
    current_player: Player = Depends(get_current_player),
):
    """Получить текущий корабль игрока."""
    if not current_player.ships:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    ship = current_player.ships[0]
    return ShipResponseDTO(
        id=ship.id,
        name=ship.name,
        tea_level=ship.tea_level.value,
        optimism=ship.optimism.value,
        speed=ship.speed,
        defense=ship.defense,
        luck=ship.luck,
    )


@router.post("/refuel", response_model=RefuelShipResponseDTO)
@limiter.limit("30/minute")
async def refuel_ship(
    request: Request,
    dto: RefuelShipDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    """Автоматически находит топливо (consumable с restore_tea) в инвентаре и заправляет корабль."""
    use_case = RefuelShipUseCase(player_repo, inventory_repo, item_repo)
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repair", response_model=RepairShipResponseDTO)
@limiter.limit("30/minute")
async def repair_ship(
    request: Request,
    dto: RepairShipDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    """Автоматически находит ремкомплект (consumable с restore_optimism) в инвентаре и чинит корабль."""
    use_case = RepairShipUseCase(player_repo, inventory_repo, item_repo)
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
