from app.application.dtos.zone_dto import ZoneResponseDTO
from app.domain.repositories.zone_repository import ZoneRepository
from app.infrastructure.cache.redis_client import redis_client


class GetZonesUseCase:
    def __init__(self, zone_repo: ZoneRepository):
        self.zone_repo = zone_repo

    async def execute(self) -> list[ZoneResponseDTO]:
        cache_key = "zones:all"

        cached = await redis_client.get(cache_key)
        if cached:
            return [ZoneResponseDTO.model_validate(z) for z in cached]

        zones = await self.zone_repo.get_all()
        result = [ZoneResponseDTO.model_validate(zone) for zone in zones]

        await redis_client.set(cache_key, [r.model_dump(mode="json") for r in result], ex=300)

        return result
