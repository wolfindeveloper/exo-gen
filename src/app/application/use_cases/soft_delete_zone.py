from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.exceptions.zone import ZoneNotFoundError


class SoftDeleteZoneUseCase:
    def __init__(self, zone_repo: ZoneRepository):
        self.zone_repo = zone_repo

    async def execute(self, zone_id: UUID, uow: UnitOfWork) -> None:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone or zone.is_deleted():
            raise ZoneNotFoundError(f"Zone {zone_id} not found")

        zone.soft_delete()
        uow.track(zone)
        await self.zone_repo.save(zone)
        await uow.commit()
