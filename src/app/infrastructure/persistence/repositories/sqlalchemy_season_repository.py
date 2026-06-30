from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.domain.repositories.season_repository import SeasonRepository
from app.domain.entities.season import Season
from app.infrastructure.persistence.models.season_orm import SeasonORM
from app.infrastructure.persistence.mappers import SeasonMapper


class SQLAlchemySeasonRepository(SeasonRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, season: Season) -> None:
        season_orm = SeasonMapper.season_to_orm(season)
        await self.session.merge(season_orm)

    async def get_by_id(self, season_id: UUID) -> Season | None:
        stmt = (
            select(SeasonORM)
            .where(SeasonORM.id == season_id)
            .where(SeasonORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return SeasonMapper.season_to_domain(orm) if orm else None

    async def get_all(self) -> list[Season]:
        stmt = (
            select(SeasonORM)
            .where(SeasonORM.deleted_at.is_(None))
            .order_by(SeasonORM.start_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [SeasonMapper.season_to_domain(o) for o in orms]

    async def get_active_seasons(self) -> list[Season]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(SeasonORM)
            .where(SeasonORM.deleted_at.is_(None))
            .where(SeasonORM.is_active)
            .where(SeasonORM.start_date <= now)
            .where(SeasonORM.end_date >= now)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [SeasonMapper.season_to_domain(o) for o in orms]
