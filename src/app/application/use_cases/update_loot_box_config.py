from uuid import UUID

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.value_objects.loot_box import LootBoxEntry
from app.domain.uow import UnitOfWork
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.exceptions.loot_box import LootBoxConfigNotFoundError
from app.application.dtos.admin_dto import UpdateLootBoxConfigDTO


class UpdateLootBoxConfigUseCase:
    def __init__(self, config_repo: LootBoxRepository):
        self.config_repo = config_repo

    async def execute(self, config_id: UUID, dto: UpdateLootBoxConfigDTO, uow: UnitOfWork) -> LootBoxConfig:
        config = await self.config_repo.get_by_id(config_id)
        if not config or config.is_deleted():
            raise LootBoxConfigNotFoundError(str(config_id))

        kwargs = dto.model_dump(exclude_none=True)
        if "entries" in kwargs:
            kwargs["entries"] = [LootBoxEntry(**e) for e in kwargs["entries"]]
        config.update(**kwargs)

        uow.track(config)
        await self.config_repo.save(config)
        await uow.commit()
        return config
