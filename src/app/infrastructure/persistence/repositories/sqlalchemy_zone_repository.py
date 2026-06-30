from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.domain.entities.zone import Zone
from app.infrastructure.persistence.models.zone_orm import ZoneORM
from app.domain.repositories.zone_repository import ZoneRepository
from app.infrastructure.persistence.mappers import ZoneMapper

_ZONE_SORT_WHITELIST = {"name", "fuel_cost", "optimism_risk", "duration_seconds"}


class SQLAlchemyZoneRepository(ZoneRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Zone]:
        result = await self.session.execute(
            select(ZoneORM).where(ZoneORM.deleted_at.is_(None))
        )
        zones_orm = result.scalars().all()
        return [ZoneMapper.zone_to_domain(z) for z in zones_orm]

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Zone], int]:
        base = select(ZoneORM).where(ZoneORM.deleted_at.is_(None))

        if search:
            base = base.where(ZoneORM.name.ilike(f"%{search}%"))

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        if sort_by in _ZONE_SORT_WHITELIST:
            column = getattr(ZoneORM, sort_by)
            base = base.order_by(column.desc() if sort_order == "desc" else column.asc())

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)

        result = await self.session.execute(base)
        zones_orm = result.scalars().all()
        return [ZoneMapper.zone_to_domain(z) for z in zones_orm], total

    async def get_by_id(self, zone_id: UUID) -> Zone | None:
        result = await self.session.execute(
            select(ZoneORM)
            .where(ZoneORM.id == zone_id)
            .where(ZoneORM.deleted_at.is_(None))
        )

        zone_orm = result.scalar_one_or_none()

        if not zone_orm:
            return None

        return ZoneMapper.zone_to_domain(zone_orm=zone_orm)

    async def save(self, zone: Zone) -> None:
        zone_orm = ZoneMapper.zone_to_orm(zone)
        await self.session.merge(zone_orm)