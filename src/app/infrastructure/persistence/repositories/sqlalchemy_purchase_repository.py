from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.persistence.models.shop_orm import PurchaseHistoryORM, ShopItemORM


class SQLAlchemyPurchaseRepository(PurchaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_shop_item(self, shop_item_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(PurchaseHistoryORM)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_shop_item_today(self, shop_item_id: UUID) -> int:
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        stmt = (
            select(func.count())
            .select_from(PurchaseHistoryORM)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
            .where(PurchaseHistoryORM.purchased_at >= day_start)
            .where(PurchaseHistoryORM.purchased_at <= day_end)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def sum_xgen_by_shop_item(self, shop_item_id: UUID) -> int:
        stmt = (
            select(func.coalesce(func.sum(ShopItemORM.price_xgen), 0))
            .select_from(PurchaseHistoryORM)
            .join(ShopItemORM, ShopItemORM.id == PurchaseHistoryORM.shop_item_id)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def add(self, player_id: UUID, shop_item_id: UUID, xgen_spent: int) -> None:
        purchase = PurchaseHistoryORM(
            id=uuid4(),
            player_id=player_id,
            shop_item_id=shop_item_id,
            purchased_at=datetime.now(timezone.utc),
        )
        self.session.add(purchase)
