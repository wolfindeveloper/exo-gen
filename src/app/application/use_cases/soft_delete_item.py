from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions import ItemNotFoundError, ItemInUseError


class SoftDeleteItemUseCase:
    def __init__(
        self,
        item_repo: ItemRepository,
    ):
        self.item_repo = item_repo

    async def execute(self, item_id: UUID, uow: UnitOfWork) -> None:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.is_deleted():
            raise ItemNotFoundError(item_id)

        report = await self.item_repo.check_usage(item_id)

        if report.in_use:
            details: list[str] = []
            if report.inventory_count > 0:
                details.append(f"{report.inventory_count} player inventories")
            for zone_name in report.zone_names:
                details.append(f"loot table of zone '{zone_name}'")
            for lb_name in report.loot_box_names:
                details.append(f"loot box '{lb_name}'")
            if report.active_shop_items > 0:
                details.append(f"{report.active_shop_items} active shop items")
            raise ItemInUseError(item.name, details)

        item.soft_delete()
        uow.track(item)
        await self.item_repo.save(item)
        await uow.commit()
