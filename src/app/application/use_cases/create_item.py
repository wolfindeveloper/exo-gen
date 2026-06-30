import uuid

from app.domain.entities.item import Item
from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.application.dtos.item_dto import CreateItemDTO


class CreateItemUseCase:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def execute(self, dto: CreateItemDTO, uow: UnitOfWork) -> Item:
        effect_raw = dto.effect.model_dump() if hasattr(dto.effect, 'model_dump') else dto.effect
        item = Item(
            id=uuid.uuid4(),
            name=dto.name,
            description=dto.description,
            type=dto.type,
            rarity=dto.rarity,
            effect=effect_raw,
            is_tradable=dto.is_tradable,
            sell_price=dto.sell_price,
        )

        await self.item_repo.save(item)
        await uow.commit()

        return item
