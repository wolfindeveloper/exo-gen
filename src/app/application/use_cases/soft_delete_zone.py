from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.exceptions.zone import ZoneNotFoundError, ZoneHasActiveExpeditionsError
from app.infrastructure.cache.redis_client import redis_client


class SoftDeleteZoneUseCase:
    def __init__(
        self,
        zone_repo: ZoneRepository,
        expedition_repo: ExpeditionRepository,
    ):
        self.zone_repo = zone_repo
        self.expedition_repo = expedition_repo

    async def execute(self, zone_id: UUID, uow: UnitOfWork) -> None:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone or zone.is_deleted():
            raise ZoneNotFoundError(f"Zone {zone_id} not found")

        expedition_count = await self.expedition_repo.count_by_zone_id(zone_id)
        if expedition_count > 0:
            raise ZoneHasActiveExpeditionsError(zone.name)

        zone.soft_delete()
        uow.track(zone)
        await self.zone_repo.save(zone)
        await uow.commit()
        await redis_client.delete("zones:*")
