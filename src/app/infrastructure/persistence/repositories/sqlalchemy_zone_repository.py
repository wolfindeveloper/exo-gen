from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.zone import Zone
from app.infrastructure.persistence.models.zone_orm import ZoneORM
from app.domain.repositories.zone_repository import ZoneRepository
from app.infrastructure.persistence.mappers import ZoneMapper


class SQLAlchemyZoneRepository(ZoneRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Zone]:
        result = await self.session.execute(select(ZoneORM))
        zones_orm = result.scalars().all()
        return [ZoneMapper.zone_to_domain(z) for z in zones_orm]

    async def get_by_id(self, zone_id: UUID) -> Zone | None:
        result = await self.session.execute(
            select(ZoneORM).where(ZoneORM.id == zone_id)
        )

        zone_orm = result.scalar_one_or_none()

        if not zone_orm:
            return None

        return ZoneMapper.zone_to_domain(zone_orm=zone_orm)

    async def save(self, zone: Zone) -> None:
        zone_orm = ZoneMapper.zone_to_orm(zone)
        await self.session.merge(zone_orm)