import uuid

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.value_objects.loot_box import LootBoxEntry
from app.domain.uow import UnitOfWork
from app.domain.repositories.loot_box_repository import LootBoxRepository


class CreateLootBoxConfigUseCase:
    def __init__(self, loot_box_repo: LootBoxRepository):
        self.loot_box_repo = loot_box_repo

    async def execute(self, dto, uow: UnitOfWork) -> LootBoxConfig:
        entries = [
            LootBoxEntry(
                item_type=e["item_type"],
                amount=e["amount"],
                chance=e["chance"],
                item_id=uuid.UUID(e["item_id"]) if e.get("item_id") else None,
            )
            for e in dto.entries
        ]
        config = LootBoxConfig(
            id=uuid.uuid4(),
            box_type=dto.box_type,
            name=dto.name,
            description=dto.description,
            entries=entries,
            is_active=dto.is_active,
        )
        await self.loot_box_repo.save(config)
        await uow.commit()
        return config
