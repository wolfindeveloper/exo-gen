import uuid

from app.domain.entities.zone import Zone
from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.application.dtos.zone_dto import CreateZoneDTO
from app.infrastructure.cache.redis_client import redis_client


class CreateZoneUseCase:
    def __init__(self, zone_repo: ZoneRepository):
        self.zone_repo = zone_repo

    async def execute(self, dto: CreateZoneDTO, uow: UnitOfWork) -> Zone:
        raw_loot_table = [item.model_dump(mode='json') for item in dto.loot_table]

        zone = Zone(
            id=uuid.uuid4(),
            name=dto.name,
            description=dto.description,
            image_url=dto.image_url,
            fuel_cost=dto.fuel_cost,
            optimism_risk=dto.optimism_risk,
            duration_seconds=dto.duration_seconds,
            loot_table=raw_loot_table,
            tier=dto.tier,
        )

        await self.zone_repo.save(zone)
        await uow.commit()
        await redis_client.delete("zones:*")

        return zone

