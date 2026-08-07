from app.application.dtos.shop_dto import ShopCategoryResponseDTO
from app.domain.repositories.shop_repository import ShopCategoryRepository


class GetShopCategoriesUseCase:
    def __init__(self, category_repo: ShopCategoryRepository):
        self.category_repo = category_repo

    async def execute(self) -> list[ShopCategoryResponseDTO]:
        categories = await self.category_repo.get_all_active()
        return [ShopCategoryResponseDTO(
            id=c.id,
            name=c.name,
            slug=c.slug,
            icon=c.icon,
            sort_order=c.sort_order,
            is_active=c.is_active,
        ) for c in categories]
