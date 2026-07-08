from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.security.rate_limiter import limiter
from app.application.dtos.expedition_dto import ExpeditionResponseDTO, StartExpeditionDTO
from app.application.dtos.claim_expedition_dto import ClaimExpeditionDTO, ClaimExpeditionResponseDTO
from app.application.use_cases.claim_expedition import ClaimExpeditionUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.application.use_cases.start_expedition import StartExpeditionUseCase
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.infrastructure.telegram.security import get_current_player

from app.presentation.api.dependencies import get_player_repo, get_expedition_repo, get_zone_repo, get_inventory_repo, get_item_repo, get_uow

router = APIRouter(prefix="/expeditions", tags=["Expeditions"])


@router.get("/active", response_model=ExpeditionResponseDTO | None)
async def get_active_expedition(
    current_player: Player = Depends(get_current_player),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
):
    if not current_player.ships:
        raise HTTPException(status_code=404, detail="No ships found")
    ship_id = current_player.ships[0].id
    expedition = await expedition_repo.get_current_by_ship_id(ship_id)
    return expedition

@router.post("/start", response_model=ExpeditionResponseDTO)
@limiter.limit("10/minute")
async def start_expedition(
    request: Request,
    dto: StartExpeditionDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = StartExpeditionUseCase(
        player_repo=player_repo,
        zone_repo=zone_repo,
        expedition_repo=expedition_repo
    )
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claim", response_model=ClaimExpeditionResponseDTO)
@limiter.limit("20/minute")
async def claim_expedition(
    request: Request,
    dto: ClaimExpeditionDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = ClaimExpeditionUseCase(
        player_repo,
        zone_repo,
        expedition_repo,
        inventory_repo,
        item_repo
    )
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))