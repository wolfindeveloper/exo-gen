from uuid import UUID

from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.services.level_progression import LevelProgressionService
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
        all_ranks = await self.player_repo.get_player_all_ranks(current_player_id)

        top_xp = await self.player_repo.get_top_players_by_xp(limit=100)
        top_expeditions = await self.player_repo.get_top_players_by_total_expeditions(limit=100)
        top_artifacts = await self.player_repo.get_top_players_by_total_artifacts_found(limit=100)
        top_xgen = await self.player_repo.get_top_players_by_xgen_balance(limit=100)
        top_articles = await self.guide_progress_repo.get_top_players_by_unlocked_articles(limit=100)
        my_articles_rank = await self.guide_progress_repo.get_player_rank_by_unlocked_articles(current_player_id)

        return GlobalLeaderboardDTO(
            my_rank=all_ranks["xp"],
            top_players=[
                PlayerShortStatsDTO(
                    rank=idx + 1,
                    telegram_id=telegram_id,
                    username=username,
                    xp=xp,
                    level=LevelProgressionService.calculate_level(xp),
                )
                for idx, (username, xp, telegram_id, _) in enumerate(top_xp)
            ],
            expeditions=MetricLeaderboardDTO(
                my_rank=all_ranks["expeditions"],
                top=[
                    MetricEntryDTO(rank=idx + 1, telegram_id=telegram_id, username=username, value=value)
                    for idx, (username, value, telegram_id, _) in enumerate(top_expeditions)
                ],
            ),
            artifacts=MetricLeaderboardDTO(
                my_rank=all_ranks["artifacts"],
                top=[
                    MetricEntryDTO(rank=idx + 1, telegram_id=telegram_id, username=username, value=value)
                    for idx, (username, value, telegram_id, _) in enumerate(top_artifacts)
                ],
            ),
            xgen=MetricLeaderboardDTO(
                my_rank=all_ranks["xgen"],
                top=[
                    MetricEntryDTO(rank=idx + 1, telegram_id=telegram_id, username=username, value=value)
                    for idx, (username, value, telegram_id, _) in enumerate(top_xgen)
                ],
            ),
            articles=MetricLeaderboardDTO(
                my_rank=my_articles_rank,
                top=[
                    MetricEntryDTO(rank=idx + 1, telegram_id=telegram_id, username=username, value=value)
                    for idx, (username, value, telegram_id, _) in enumerate(top_articles)
                ],
            ),
        )
