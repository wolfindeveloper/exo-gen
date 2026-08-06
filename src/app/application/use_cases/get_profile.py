from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.application.dtos.profile_dto import ProfileResponseDTO
from app.domain.entities.player import Player
from app.domain.services.level_progression import LevelProgressionService
from app.infrastructure.cache.redis_client import redis_client


class GetProfileUseCase:
    def __init__(
        self,
        guide_progress_repo: GuideProgressRepository,
        chapter_repo: ChapterRepository | None = None,
        expedition_repo: ExpeditionRepository | None = None,
    ):
        self.guide_progress_repo = guide_progress_repo
        self.chapter_repo = chapter_repo
        self.expedition_repo = expedition_repo

    async def execute(self, player: Player) -> ProfileResponseDTO:
        cache_key = f"profile:{player.id}"
        cached = await redis_client.get(cache_key)
        if cached:
            return ProfileResponseDTO.model_validate(cached)

        unlocked_ids = await self.guide_progress_repo.get_unlocked_articles_ids(
            player.id
        )

        _, articles_total = (
            await self.chapter_repo.get_paginated_articles(page=1, page_size=1)
            if self.chapter_repo
            else (None, 0)
        )

        expeditions_in_progress = 0
        if self.expedition_repo and player.ships:
            ship_id = player.ships[0].id
            active_exp = await self.expedition_repo.get_current_by_ship_id(ship_id)
            if active_exp is not None:
                expeditions_in_progress = 1

        profile = ProfileResponseDTO(
            xp=player.xp,
            level=LevelProgressionService.calculate_level(player.xp),
            total_expeditions=player.total_expeditions,
            total_artifacts_found=player.total_artifacts_found,
            unlocked_articles=len(unlocked_ids),
            expeditions_completed=player.total_expeditions,
            expeditions_in_progress=expeditions_in_progress,
            artifacts_found=player.total_artifacts_found,
            xgen_earned_total=player.xgen_balance.value,
            articles_read=len(unlocked_ids),
            articles_total=articles_total,
        )

        await redis_client.set(cache_key, profile.model_dump(mode='json'), ex=60)

        return profile
