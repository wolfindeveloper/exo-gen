from uuid import UUID
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import LeaderboardEntryDTO


class GetLeaderboardUseCase:
    def __init__(self, progress_repo: GuideProgressRepository):
        self.progress_repo = progress_repo


    async def execute(self, season_id: UUID) -> list[LeaderboardEntryDTO]:
        entries = await self.progress_repo.get_season_leaderboard(season_id)

        # Превращаем доменные объекты в DTO для фронта
        return [
            LeaderboardEntryDTO(
                username=e.username,
                chapter_name=e.chapter_name,
                completed_at=e.completed_at
            )
            for e in entries
        ]