from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.security.rate_limiter import limiter
from app.application.dtos.expedition_dto import ExpeditionResponseDTO, StartExpeditionDTO
from app.application.dtos.claim_expedition_dto import ClaimExpeditionDTO, ClaimExpeditionResponseDTO
from app.application.use_cases.claim_expedition import ClaimExpeditionUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.application.use_cases.start_expedition import StartExpeditionUseCase
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.telegram.security import get_current_player

from app.presentation.api.dependencies import get_player_repo, get_expedition_repo, get_zone_repo, get_inventory_repo, get_uow

router = APIRouter(prefix="/expeditions", tags=["Expeditions"])

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
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = ClaimExpeditionUseCase(
        player_repo,
        zone_repo,
        expedition_repo,
        inventory_repo
    )
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))