from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions import ItemNotFoundError


class SoftDeleteItemUseCase:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def execute(self, item_id: UUID, uow: UnitOfWork) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.is_deleted():
            raise ItemNotFoundError(item_id)

        item.soft_delete()
        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
