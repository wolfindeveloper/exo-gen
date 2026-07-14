from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.profile_dto import ProfileResponseDTO
from app.domain.entities.player import Player
from app.domain.services.level_progression import LevelProgressionService


class GetProfileUseCase:
    def __init__(
        self,
        guide_progress_repo: GuideProgressRepository,
    ):
        self.guide_progress_repo = guide_progress_repo

    async def execute(self, player: Player) -> ProfileResponseDTO:
        unlocked_ids = await self.guide_progress_repo.get_unlocked_articles_ids(
            player.id
        )

        return ProfileResponseDTO(
            xp=player.xp,
            level=LevelProgressionService.calculate_level(player.xp),
            total_expeditions=player.total_expeditions,
            total_artifacts_found=player.total_artifacts_found,
            unlocked_articles=len(unlocked_ids),
        )
