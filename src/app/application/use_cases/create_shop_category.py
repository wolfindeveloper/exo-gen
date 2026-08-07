import uuid

from app.domain.entities.shop import ShopCategory
from app.domain.uow import UnitOfWork
from app.domain.repositories.shop_repository import ShopCategoryRepository
from app.domain.exceptions.shop import ShopCategorySlugTakenError
from app.application.dtos.shop_dto import CreateShopCategoryDTO


class CreateShopCategoryUseCase:
    def __init__(self, category_repo: ShopCategoryRepository):
        self.category_repo = category_repo

    async def execute(self, dto: CreateShopCategoryDTO, uow: UnitOfWork) -> ShopCategory:
        existing = await self.category_repo.get_by_slug(dto.slug)
        if existing is not None:
            raise ShopCategorySlugTakenError(dto.slug)

        category = ShopCategory(
            id=uuid.uuid4(),
            name=dto.name,
            slug=dto.slug,
            icon=dto.icon,
            sort_order=dto.sort_order,
            is_active=True,
        )

        await self.category_repo.save(category)
        await uow.commit()

        return category
