from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.exceptions.shop import ShopItemNotFoundError


class SoftDeleteShopItemUseCase:
    def __init__(self, shop_item_repo: ShopItemRepository):
        self.shop_item_repo = shop_item_repo

    async def execute(self, shop_item_id: UUID, uow: UnitOfWork) -> None:
        shop_item = await self.shop_item_repo.get_by_id(shop_item_id)
        if not shop_item or shop_item.is_deleted():
            raise ShopItemNotFoundError(shop_item_id)

        shop_item.soft_delete()
        uow.track(shop_item)
        await self.shop_item_repo.save(shop_item)
        await uow.commit()
