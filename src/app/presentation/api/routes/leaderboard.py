from fastapi import APIRouter, Depends
from app.domain.repositories.player_repository import PlayerRepository
from app.application.use_cases.get_global_leaderboard import GetGlobalLeaderboardUseCase
from app.application.dtos.leaderboard_dto import GlobalLeaderboardDTO
from app.domain.entities.player import Player
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_player_repo

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/global", response_model=GlobalLeaderboardDTO)
async def get_global_leaderboard(
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
):
    use_case = GetGlobalLeaderboardUseCase(player_repo)
    return await use_case.execute(current_player.id)
