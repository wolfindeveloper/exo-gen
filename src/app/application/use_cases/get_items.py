from app.domain.repositories.item_repository import ItemRepository
from app.application.dtos.item_dto import ItemResponseDTO

class GetItemsUseCase:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def execute(self) -> list[ItemResponseDTO]:
        items = await self.item_repo.get_all()
        return [
            ItemResponseDTO(
                id=i.id,
                name=i.name,
                description=i.description,
                type=i.type,
                rarity=i.rarity,
                effect=i.effect,
                is_tradable=i.is_tradable,
                sell_price=i.sell_price,
                image_url=i.image_url or "",
            ) for i in items
        ]