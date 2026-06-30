from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.exceptions.guide import SeasonNotFoundError


class SoftDeleteSeasonUseCase:
    def __init__(self, season_repo: SeasonRepository):
        self.season_repo = season_repo

    async def execute(self, season_id: UUID, uow: UnitOfWork) -> None:
        season = await self.season_repo.get_by_id(season_id)
        if not season or season.is_deleted():
            raise SeasonNotFoundError(str(season_id))

        season.soft_delete()
        uow.track(season)
        await self.season_repo.save(season)
        await uow.commit()
