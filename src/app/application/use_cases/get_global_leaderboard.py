from uuid import UUID

from app.domain.repositories.player_repository import PlayerRepository
from app.domain.services.level_progression import LevelProgressionService
from app.application.dtos.leaderboard_dto import (
    GlobalLeaderboardDTO,
    PlayerShortStatsDTO,
)


class GetGlobalLeaderboardUseCase:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    async def execute(self, current_player_id: UUID) -> GlobalLeaderboardDTO:
        top_players = await self.player_repo.get_top_players_by_xp(limit=100)
        my_rank = await self.player_repo.get_player_rank_by_xp(current_player_id)

        top_players_dtos = [
            PlayerShortStatsDTO(
                rank=idx + 1,
                username=username,
                xp=xp,
                level=LevelProgressionService.calculate_level(xp),
            )
            for idx, (username, xp, _) in enumerate(top_players)
        ]

        return GlobalLeaderboardDTO(
            my_rank=my_rank,
            top_players=top_players_dtos,
        )
