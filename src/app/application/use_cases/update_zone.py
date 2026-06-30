from uuid import UUID

from app.domain.entities.zone import Zone
from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.exceptions.zone import ZoneNotFoundError
from app.application.dtos.admin_dto import UpdateZoneDTO


class UpdateZoneUseCase:
    def __init__(self, zone_repo: ZoneRepository):
        self.zone_repo = zone_repo

    async def execute(self, zone_id: UUID, dto: UpdateZoneDTO, uow: UnitOfWork) -> Zone:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone or zone.is_deleted():
            raise ZoneNotFoundError(f"Zone {zone_id} not found")

        zone.update(**dto.model_dump(exclude_none=True))

        uow.track(zone)
        await self.zone_repo.save(zone)
        await uow.commit()
        return zone
