from fastapi import APIRouter, Depends
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.use_cases.get_global_leaderboard import GetGlobalLeaderboardUseCase
from app.application.use_cases.get_multi_metric_leaderboard import GetMultiMetricLeaderboardUseCase
from app.application.dtos.leaderboard_dto import GlobalLeaderboardDTO
from app.domain.entities.player import Player
from app.infrastructure.telegram.security import get_current_player
from app.presentation.api.dependencies import get_player_repo, get_guide_progress_repo

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/global", response_model=GlobalLeaderboardDTO)
async def get_global_leaderboard(
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
):
    use_case = GetGlobalLeaderboardUseCase(player_repo)
    return await use_case.execute(current_player.id)


@router.get("/multi-metric", response_model=GlobalLeaderboardDTO)
async def get_multi_metric_leaderboard(
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    guide_progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
):
    use_case = GetMultiMetricLeaderboardUseCase(player_repo, guide_progress_repo)
    return await use_case.execute(current_player.id)
