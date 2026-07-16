from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.application.dtos.profile_dto import ProfileResponseDTO
from app.domain.entities.player import Player
from app.domain.services.level_progression import LevelProgressionService


class GetProfileUseCase:
    def __init__(
        self,
        guide_progress_repo: GuideProgressRepository,
        chapter_repo: ChapterRepository | None = None,
    ):
        self.guide_progress_repo = guide_progress_repo
        self.chapter_repo = chapter_repo

    async def execute(self, player: Player) -> ProfileResponseDTO:
        unlocked_ids = await self.guide_progress_repo.get_unlocked_articles_ids(
            player.id
        )

        _, articles_total = (
            await self.chapter_repo.get_paginated_articles(page=1, page_size=1)
            if self.chapter_repo
            else (None, 0)
        )

        return ProfileResponseDTO(
            xp=player.xp,
            level=LevelProgressionService.calculate_level(player.xp),
            total_expeditions=player.total_expeditions,
            total_artifacts_found=player.total_artifacts_found,
            unlocked_articles=len(unlocked_ids),
            expeditions_completed=player.total_expeditions,
            expeditions_in_progress=0,
            artifacts_found=player.total_artifacts_found,
            xgen_earned_total=player.xgen_balance.value,
            articles_read=len(unlocked_ids),
            articles_total=articles_total,
        )
