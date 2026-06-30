import uuid

from app.domain.entities.season import Season
from app.domain.uow import UnitOfWork
from app.domain.repositories.season_repository import SeasonRepository
from app.application.dtos.guide_dto import CreateSeasonDTO


class CreateSeasonUseCase:
    def __init__(self, season_repo: SeasonRepository):
        self.season_repo = season_repo

    async def execute(self, dto: CreateSeasonDTO, uow: UnitOfWork) -> Season:
        season = Season(
            id=uuid.uuid4(),
            name=dto.name,
            description=dto.description,
            start_date=dto.start_date,
            end_date=dto.end_date,
            reward_xgen=dto.reward_xgen,
            reward_fragments=dto.reward_fragments,
            is_active=dto.is_active,
        )

        await self.season_repo.save(season)
        await uow.commit()

        return season
