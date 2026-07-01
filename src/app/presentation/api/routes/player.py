from fastapi import APIRouter, Depends, HTTPException, Request
from app.config.settings import settings
from app.infrastructure.security.rate_limiter import limiter
from app.application.dtos.player_dto import CreatePlayerDTO
from app.application.dtos.player_response_dto import PlayerResponseDTO
from app.application.dtos.profile_dto import ProfileResponseDTO
from app.application.use_cases.create_player import CreatePlayerUseCase
from app.application.use_cases.get_player import GetPlayerUseCase
from app.application.use_cases.process_daily_login import ProcessDailyLoginUseCase
from app.application.use_cases.get_profile import GetProfileUseCase
from app.domain.entities.player import Player
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import (
    get_player_repo,
    get_guide_progress_repo,
    get_inventory_repo,
    get_item_repo,
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


@router.get("/me", response_model=PlayerResponseDTO)
async def get_player(
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
):
    use_case = GetPlayerUseCase(player_repo=player_repo)
    player = await use_case.execute(telegram_id=current_player.telegram_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@router.get("/me/profile", response_model=ProfileResponseDTO)
async def get_profile(
    current_player: Player = Depends(get_current_player),
    guide_progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
):
    use_case = GetProfileUseCase(guide_progress_repo)
    return await use_case.execute(current_player)


@router.get("/me/admin-status")
async def get_admin_status(
    current_player: Player = Depends(get_current_player),
):
    is_admin = current_player.telegram_id in settings.ADMIN_TELEGRAM_IDS
    return {"is_admin": is_admin}


@router.post("/daily-login")
@limiter.limit("5/minute")
async def daily_login(
    request: Request,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = ProcessDailyLoginUseCase(
        player_repo=player_repo,
        loot_box_service=LootBoxService(),
        loot_box_repo=loot_box_repo,
        inventory_repo=inventory_repo,
        item_repo=item_repo,
    )
    try:
        result = await use_case.execute(current_player.telegram_id, uow)
        return result
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))
