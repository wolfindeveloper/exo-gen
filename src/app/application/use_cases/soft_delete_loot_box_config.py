from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.exceptions.loot_box import LootBoxConfigNotFoundError


class SoftDeleteLootBoxConfigUseCase:
    def __init__(self, config_repo: LootBoxRepository):
        self.config_repo = config_repo

    async def execute(self, config_id: UUID, uow: UnitOfWork) -> None:
        config = await self.config_repo.get_by_id(config_id)
        if not config or config.is_deleted():
            raise LootBoxConfigNotFoundError(str(config_id))

        config.soft_delete()
        uow.track(config)
        await self.config_repo.save(config)
        await uow.commit()
