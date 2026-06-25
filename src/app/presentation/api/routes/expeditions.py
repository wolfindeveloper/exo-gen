from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos.expedition_dto import ExpeditionResponseDTO, StartExpeditionDTO
from app.application.dtos.claim_expedition_dto import ClaimExpeditionDTO, ClaimExpeditionResponseDTO
from app.application.use_cases.claim_expedition import ClaimExpeditionUseCase
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.application.use_cases.start_expedition import StartExpeditionUseCase
from app.domain.repositories.inventory_repository import InventoryRepository

from app.presentation.api.dependencies import get_player_repo, get_expedition_repo, get_zone_repo, get_inventory_repo

router = APIRouter(prefix="/expeditions", tags=["Expeditions"])

@router.post("/start", response_model=ExpeditionResponseDTO)
async def start_expedition(
    dto: StartExpeditionDTO,
    player_repo: PlayerRepository = Depends(get_player_repo),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo) # Не забудь добавить в dependencies.py!
):
    use_case = StartExpeditionUseCase(
        player_repo=player_repo, 
        zone_repo=zone_repo, 
        expedition_repo=expedition_repo
    )
    try:
        return await use_case.execute(dto)
    except ValueError as e:
        # Любая бизнес-ошибка (нет топлива, корабль уже летит) вернет 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claim", response_model=ClaimExpeditionResponseDTO)
async def claim_expedition(
    dto: ClaimExpeditionDTO,
    player_repo: PlayerRepository = Depends(get_player_repo),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo) # <-- ДОБАВИЛИ
):
    use_case = ClaimExpeditionUseCase(
        player_repo, 
        zone_repo, 
        expedition_repo, 
        inventory_repo # <-- ПЕРЕДАЛИ
    )
    try:
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))