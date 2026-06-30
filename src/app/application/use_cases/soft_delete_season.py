from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.exceptions.guide import SeasonNotFoundError, SeasonActiveError, SeasonHasProgressError


class SoftDeleteSeasonUseCase:
    def __init__(
        self,
        season_repo: SeasonRepository,
        chapter_repo: ChapterRepository,
        guide_progress_repo: GuideProgressRepository,
    ):
        self.season_repo = season_repo
        self.chapter_repo = chapter_repo
        self.guide_progress_repo = guide_progress_repo

    async def execute(self, season_id: UUID, uow: UnitOfWork) -> None:
        season = await self.season_repo.get_by_id(season_id)
        if not season or season.is_deleted():
            raise SeasonNotFoundError(str(season_id))

        if season.is_currently_active():
            raise SeasonActiveError(season.name)

        chapters = await self.chapter_repo.get_by_season_id(season.id)
        if chapters:
            chapter_ids = [c.id for c in chapters]
            unlocked_count = await self.guide_progress_repo.count_unlocked_by_chapter_ids(chapter_ids)
            if unlocked_count > 0:
                raise SeasonHasProgressError(season.name)

        season.soft_delete()
        uow.track(season)
        await self.season_repo.save(season)
        await uow.commit()
