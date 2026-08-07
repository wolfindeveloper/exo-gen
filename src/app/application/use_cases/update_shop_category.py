from uuid import UUID

from app.domain.entities.shop import ShopCategory
from app.domain.uow import UnitOfWork
from app.domain.repositories.shop_repository import ShopCategoryRepository
from app.domain.exceptions.shop import ShopCategoryNotFoundError
from app.application.dtos.shop_dto import UpdateShopCategoryDTO


class UpdateShopCategoryUseCase:
    def __init__(self, category_repo: ShopCategoryRepository):
        self.category_repo = category_repo

    async def execute(self, category_id: UUID, dto: UpdateShopCategoryDTO, uow: UnitOfWork) -> ShopCategory:
        category = await self.category_repo.get_by_id(category_id)
        if not category or category.is_deleted():
            raise ShopCategoryNotFoundError(category_id)

        category.update(**dto.model_dump(exclude_none=True))

        uow.track(category)
        await self.category_repo.save(category)
        await uow.commit()
        return category
