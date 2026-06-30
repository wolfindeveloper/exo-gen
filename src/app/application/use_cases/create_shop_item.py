from uuid import UUID, uuid4

from app.domain.uow import UnitOfWork
from app.application.dtos.admin_dto import CreateShopItemDTO


class CreateShopItem:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, data: CreateShopItemDTO) -> dict:
        async with self.uow:
            shop_data = data.model_dump(exclude_unset=True)
            shop_data.setdefault("id", uuid4())

            bundle_items = shop_data.get("bundle_items", [])
            if bundle_items:
                for item in bundle_items:
                    if isinstance(item.get("item_id"), UUID):
                        item["item_id"] = str(item["item_id"])

                shop_data["item_id"] = None

            created_item = await self.uow.shop.add(shop_data)
            await self.uow.commit()

            return created_item
