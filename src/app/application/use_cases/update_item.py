from uuid import UUID

from app.domain.entities.item import Item, ItemType
from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions import ItemNotFoundError
from app.application.dtos.admin_dto import UpdateItemDTO, ConsumableEffectDTO, ArtifactEffectDTO


class UpdateItemUseCase:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def execute(self, item_id: UUID, dto: UpdateItemDTO, uow: UnitOfWork) -> Item:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.is_deleted():
            raise ItemNotFoundError(item_id)

        if dto.effect is not None:
            if item.type == ItemType.CONSUMABLE and not isinstance(dto.effect, ConsumableEffectDTO):
                raise ValueError("Consumable items can only have consumable effects (restore_tea, restore_optimism)")
            if item.type == ItemType.ARTIFACT and not isinstance(dto.effect, ArtifactEffectDTO):
                raise ValueError("Artifact items can only have artifact effects (bonus_*)")

        item.update(**dto.model_dump(exclude_none=True))

        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
        return item
