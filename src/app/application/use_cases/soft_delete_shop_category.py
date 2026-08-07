from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.shop_repository import ShopCategoryRepository
from app.domain.exceptions.shop import (
    ShopCategoryNotFoundError,
    ShopCategoryHasItemsError,
)


class SoftDeleteShopCategoryUseCase:
    def __init__(self, category_repo: ShopCategoryRepository):
        self.category_repo = category_repo

    async def execute(self, category_id: UUID, uow: UnitOfWork) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if not category or category.is_deleted():
            raise ShopCategoryNotFoundError(category_id)

        item_count = await self.category_repo.count_items_by_category(category_id)
        if item_count > 0:
            raise ShopCategoryHasItemsError(category_id)

        category.soft_delete()
        uow.track(category)
        await self.category_repo.save(category)
        await uow.commit()
