from uuid import UUID
from random import SystemRandom

from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions.loot_box import LootBoxConfigNotFoundError
from app.application.dtos.simulation_dto import LootBoxSimulationResultDTO

_rng = SystemRandom()


class SimulateLootBoxUseCase:
    def __init__(
        self,
        loot_box_repo: LootBoxRepository,
        item_repo: ItemRepository,
    ):
        self.loot_box_repo = loot_box_repo
        self.item_repo = item_repo

    async def execute(self, config_id: UUID, count: int) -> list[LootBoxSimulationResultDTO]:
        config = await self.loot_box_repo.get_by_id(config_id)
        if not config or config.is_deleted():
            raise LootBoxConfigNotFoundError(str(config_id))

        entries = config.entries
        if not entries:
            return []

        hits = [0] * len(entries)
        total_xgen = 0
        total_fragments = 0

        for _ in range(count):
            for i, entry in enumerate(entries):
                if _rng.random() < entry.chance:
                    hits[i] += 1
                    if entry.item_type == "xgen":
                        total_xgen += entry.amount
                    elif entry.item_type == "fragments":
                        total_fragments += entry.amount

        item_ids = set()
        for entry in entries:
            if entry.item_type == "item" and entry.item_id:
                item_ids.add(entry.item_id)

        items_map: dict[UUID, str] = {}
        if item_ids:
            items = await self.item_repo.get_by_ids(list(item_ids))
            items_map = {it.id: it.name for it in items if not it.is_deleted()}

        results = []
        for i, entry in enumerate(entries):
            item_id = entry.item_id if entry.item_type == "item" else None
            item_name = items_map.get(entry.item_id) if entry.item_id and entry.item_type == "item" else None

            results.append(
                LootBoxSimulationResultDTO(
                    drop_type=entry.item_type,
                    item_id=item_id,
                    item_name=item_name,
                    total_dropped=hits[i],
                    percentage=round(hits[i] / count * 100, 2),
                    total_xgen=total_xgen,
                    total_fragments=total_fragments,
                )
            )

        return results
