from uuid import UUID

from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.leaderboard_dto import (
    GlobalLeaderboardDTO,
    PlayerShortStatsDTO,
    MetricLeaderboardDTO,
    MetricEntryDTO,
)


class GetMultiMetricLeaderboardUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        guide_progress_repo: GuideProgressRepository,
    ):
        self.player_repo = player_repo
        self.guide_progress_repo = guide_progress_repo

    async def execute(self, current_player_id: UUID) -> GlobalLeaderboardDTO:
        top_xp = await self.player_repo.get_top_players_by_xp(limit=100)
        my_xp_rank = await self.player_repo.get_player_rank_by_xp(current_player_id)

        top_expeditions = await self.player_repo.get_top_players_by_total_expeditions(limit=100)
        my_expeditions_rank = await self.player_repo.get_player_rank_by_total_expeditions(current_player_id)

        top_artifacts = await self.player_repo.get_top_players_by_total_artifacts_found(limit=100)
        my_artifacts_rank = await self.player_repo.get_player_rank_by_total_artifacts_found(current_player_id)

        top_xgen = await self.player_repo.get_top_players_by_xgen_balance(limit=100)
        my_xgen_rank = await self.player_repo.get_player_rank_by_xgen_balance(current_player_id)

        top_articles = await self.guide_progress_repo.get_top_players_by_unlocked_articles(limit=100)
        my_articles_rank = await self.guide_progress_repo.get_player_rank_by_unlocked_articles(current_player_id)

        return GlobalLeaderboardDTO(
            my_rank=my_xp_rank,
            top_players=[
                PlayerShortStatsDTO(
                    rank=idx + 1,
                    username=username,
                    xp=xp,
                    level=xp // 1000,
                )
                for idx, (username, xp, _) in enumerate(top_xp)
            ],
            expeditions=MetricLeaderboardDTO(
                my_rank=my_expeditions_rank,
                top=[
                    MetricEntryDTO(rank=idx + 1, username=username, value=value)
                    for idx, (username, value, _) in enumerate(top_expeditions)
                ],
            ),
            artifacts=MetricLeaderboardDTO(
                my_rank=my_artifacts_rank,
                top=[
                    MetricEntryDTO(rank=idx + 1, username=username, value=value)
                    for idx, (username, value, _) in enumerate(top_artifacts)
                ],
            ),
            xgen=MetricLeaderboardDTO(
                my_rank=my_xgen_rank,
                top=[
                    MetricEntryDTO(rank=idx + 1, username=username, value=value)
                    for idx, (username, value, _) in enumerate(top_xgen)
                ],
            ),
            articles=MetricLeaderboardDTO(
                my_rank=my_articles_rank,
                top=[
                    MetricEntryDTO(rank=idx + 1, username=username, value=value)
                    for idx, (username, value, _) in enumerate(top_articles)
                ],
            ),
        )
