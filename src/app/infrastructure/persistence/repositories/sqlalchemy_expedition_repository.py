from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.expedition import Expedition
from app.infrastructure.persistence.models.expedition_orm import ExpeditionORM
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.infrastructure.persistence.mappers import ExpeditionMapper


class SQLAlchemyExpeditionRepository(ExpeditionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_ship_id(self, ship_id: UUID) -> Expedition | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(ExpeditionORM)
            .where(ExpeditionORM.ship_id == ship_id,
            ExpeditionORM.ends_at > now
            )
            .order_by(ExpeditionORM.started_at.desc())
            .limit(1)
            .with_for_update()
        )
        result = await self.session.execute(stmt)

        expedition_orm = result.scalar_one_or_none()

        if not expedition_orm:
            return None

        return ExpeditionMapper.expedition_to_domain(expedition_orm=expedition_orm)

    async def get_by_id(self, expedition_id: UUID) -> Expedition | None:
        result = await self.session.execute(
            select(ExpeditionORM).where(ExpeditionORM.id == expedition_id)
        )

        expedition_orm = result.scalar_one_or_none()

        if not expedition_orm:
            return None

        return ExpeditionMapper.expedition_to_domain(expedition_orm=expedition_orm)

    async def get_finished_expeditions(self) -> list[Expedition]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(ExpeditionORM)
            .where(
                ExpeditionORM.status == "in_progress",
                ExpeditionORM.ends_at <= now,
            )
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        expeditions_orm = result.scalars().all()
        return [
            ExpeditionMapper.expedition_to_domain(e) for e in expeditions_orm
        ]

    async def save(self, expedition: Expedition) -> None:
        expedition_orm = ExpeditionMapper.expedition_to_orm(expedition)
        await self.session.merge(expedition_orm)