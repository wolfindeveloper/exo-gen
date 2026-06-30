from uuid import UUID
from random import SystemRandom

from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions.zone import ZoneNotFoundError
from app.application.dtos.simulation_dto import LootSimulationResultDTO

_rng = SystemRandom()


class SimulateZoneLootUseCase:
    def __init__(
        self,
        zone_repo: ZoneRepository,
        item_repo: ItemRepository,
    ):
        self.zone_repo = zone_repo
        self.item_repo = item_repo

    async def execute(self, zone_id: UUID, count: int) -> list[LootSimulationResultDTO]:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone or zone.is_deleted():
            raise ZoneNotFoundError(f"Zone {zone_id} not found")

        loot_table = zone.loot_table or []
        if not loot_table:
            return []

        hits = [0] * len(loot_table)

        for _ in range(count):
            for i, entry in enumerate(loot_table):
                if _rng.random() < entry.get("chance", 0):
                    hits[i] += 1

        item_ids = set()
        for entry in loot_table:
            raw_id = entry.get("item_id")
            if raw_id:
                try:
                    item_ids.add(UUID(str(raw_id)))
                except ValueError:
                    pass

        items_map: dict[UUID, str] = {}
        if item_ids:
            items = await self.item_repo.get_by_ids(list(item_ids))
            items_map = {it.id: it.name for it in items if not it.is_deleted()}

        results = []
        for i, entry in enumerate(loot_table):
            drop_type = entry.get("drop_type") or entry.get("item_type", "unknown")
            item_id: UUID | None = None
            item_name: str | None = None
            raw_id = entry.get("item_id")
            if raw_id:
                try:
                    parsed = UUID(str(raw_id))
                    item_id = parsed
                    item_name = items_map.get(parsed)
                except ValueError:
                    pass

            results.append(
                LootSimulationResultDTO(
                    drop_type=drop_type,
                    item_id=item_id,
                    item_name=item_name,
                    total_dropped=hits[i],
                    percentage=round(hits[i] / count * 100, 2),
                )
            )

        return results
