from uuid import UUID

from app.domain.entities.season import Season
from app.domain.uow import UnitOfWork
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.exceptions.guide import SeasonNotFoundError
from app.application.dtos.admin_dto import UpdateSeasonDTO


class UpdateSeasonUseCase:
    def __init__(self, season_repo: SeasonRepository):
        self.season_repo = season_repo

    async def execute(self, season_id: UUID, dto: UpdateSeasonDTO, uow: UnitOfWork) -> Season:
        season = await self.season_repo.get_by_id(season_id)
        if not season or season.is_deleted():
            raise SeasonNotFoundError(str(season_id))

        season.update(**dto.model_dump(exclude_none=True))

        uow.track(season)
        await self.season_repo.save(season)
        await uow.commit()
        return season
