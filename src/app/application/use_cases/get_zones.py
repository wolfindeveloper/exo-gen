from uuid import UUID

from app.application.dtos.zone_dto import ZoneResponseDTO
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.infrastructure.cache.redis_client import redis_client


class GetZonesUseCase:
    def __init__(self, zone_repo: ZoneRepository, item_repo: ItemRepository):
        self.zone_repo = zone_repo
        self.item_repo = item_repo

    async def execute(self) -> list[ZoneResponseDTO]:
        cache_key = "zones:all"

        cached = await redis_client.get(cache_key)
        if cached:
            return [ZoneResponseDTO.model_validate(z) for z in cached]

        zones = await self.zone_repo.get_all()
        result = [ZoneResponseDTO.model_validate(zone) for zone in zones]

        item_ids = set()
        for zone_dto in result:
            for loot in zone_dto.loot_table:
                if loot.item_type == "item" and loot.item_id:
                    try:
                        item_ids.add(UUID(loot.item_id))
                    except ValueError:
                        pass

        if item_ids:
            items = await self.item_repo.get_by_ids(list(item_ids))
            item_map = {str(it.id): it.name for it in items if not it.is_deleted()}
            for zone_dto in result:
                for loot in zone_dto.loot_table:
                    if loot.item_type == "item" and loot.item_id in item_map:
                        loot.item_name = item_map[loot.item_id]

        await redis_client.set(cache_key, [r.model_dump(mode="json") for r in result], ex=300)

        return result
