from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.profile_dto import ProfileResponseDTO
from app.domain.entities.player import Player


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
            level=player.xp // 1000,
            total_expeditions=player.total_expeditions,
            total_artifacts_found=player.total_artifacts_found,
            unlocked_articles=len(unlocked_ids),
        )
