from fastapi import APIRouter, Depends

from app.domain.entities.player import Player
from app.domain.repositories.player_settings_repository import PlayerSettingsRepository
from app.application.use_cases.get_player_settings import GetPlayerSettingsUseCase
from app.application.use_cases.update_player_settings import UpdatePlayerSettingsUseCase
from app.application.dtos.player_settings_dto import (
    PlayerSettingsDTO,
    UpdatePlayerSettingsDTO,
)
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_player_settings_repo

router = APIRouter(prefix="/players/me", tags=["Settings"])


@router.get("/settings", response_model=PlayerSettingsDTO)
async def get_settings(
    current_player: Player = Depends(get_current_player),
    settings_repo: PlayerSettingsRepository = Depends(get_player_settings_repo),
):
    use_case = GetPlayerSettingsUseCase(settings_repo)
    return await use_case.execute(current_player.id)


@router.patch("/settings", response_model=PlayerSettingsDTO)
async def update_settings(
    dto: UpdatePlayerSettingsDTO,
    current_player: Player = Depends(get_current_player),
    settings_repo: PlayerSettingsRepository = Depends(get_player_settings_repo),
):
    use_case = UpdatePlayerSettingsUseCase(settings_repo)
    return await use_case.execute(current_player.id, dto)
