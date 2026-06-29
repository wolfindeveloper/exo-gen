from fastapi import APIRouter, Depends, HTTPException, Request
from app.infrastructure.security.rate_limiter import limiter
from app.application.dtos.player_dto import CreatePlayerDTO
from app.application.dtos.player_response_dto import PlayerResponseDTO
from app.application.use_cases.create_player import CreatePlayerUseCase
from app.application.use_cases.get_player import GetPlayerUseCase
from app.application.use_cases.process_daily_login import ProcessDailyLoginUseCase
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.presentation.api.dependencies import (
    get_player_repo,
    get_inventory_repo,
    get_loot_box_repo,
    get_uow,
)

router = APIRouter(prefix="/players", tags=["Players"])


@router.post("/register", status_code=201)
@limiter.limit("10/minute")
async def register_player(
    request: Request,
    dto: CreatePlayerDTO,
    player_repo: PlayerRepository = Depends(get_player_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreatePlayerUseCase(player_repo=player_repo)
    player = await use_case.execute(dto, uow)
    return {
        "id": str(player.id),
        "telegram_id": player.telegram_id,
        "ships": len(player.ships),
    }


@router.get("/telegram_id", response_model=PlayerResponseDTO)
async def get_player(
    telegram_id: int, player_repo: PlayerRepository = Depends(get_player_repo)
):

    use_case = GetPlayerUseCase(player_repo=player_repo)
    player = await use_case.execute(telegram_id=telegram_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@router.post("/{telegram_id}/daily-login")
@limiter.limit("5/minute")
async def daily_login(
    request: Request,
    telegram_id: int,
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = ProcessDailyLoginUseCase(
        player_repo=player_repo,
        loot_box_service=LootBoxService(),
        loot_box_repo=loot_box_repo,
        inventory_repo=inventory_repo,
    )
    try:
        result = await use_case.execute(telegram_id, uow)
        return result
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))
