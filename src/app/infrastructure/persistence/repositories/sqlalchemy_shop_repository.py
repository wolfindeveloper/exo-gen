from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.shop import ShopItem, PurchaseHistory
from app.domain.repositories.shop_repository import ShopItemRepository, PurchaseHistoryRepository
from app.infrastructure.persistence.mappers import ShopItemMapper, PurchaseHistoryMapper
from app.infrastructure.persistence.models.shop_orm import ShopItemORM, PurchaseHistoryORM


class SQLAlchemyShopItemRepository(ShopItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, shop_item_id: UUID) -> ShopItem | None:
        stmt = (
            select(ShopItemORM)
            .where(ShopItemORM.id == shop_item_id)
            .where(ShopItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return ShopItemMapper.to_domain(orm) if orm else None

    async def get_all(self) -> list[ShopItem]:
        stmt = (
            select(ShopItemORM)
            .where(ShopItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ShopItemMapper.to_domain(o) for o in orms]

    async def get_all_active(self) -> list[ShopItem]:
        stmt = (
            select(ShopItemORM)
            .where(ShopItemORM.is_active == True)
            .where(ShopItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ShopItemMapper.to_domain(o) for o in orms]

    async def get_all_by_item_id(self, item_id: UUID) -> list[ShopItem]:
        stmt = (
            select(ShopItemORM)
            .where(ShopItemORM.item_id == item_id)
            .where(ShopItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ShopItemMapper.to_domain(o) for o in orms]

    async def save(self, shop_item: ShopItem) -> None:
        orm_obj = ShopItemMapper.to_orm(shop_item)
        await self.session.merge(orm_obj)


class SQLAlchemyPurchaseHistoryRepository(PurchaseHistoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_and_shop_item(
        self, player_id: UUID, shop_item_id: UUID
    ) -> list[PurchaseHistory]:
        stmt = (
            select(PurchaseHistoryORM)
            .where(PurchaseHistoryORM.player_id == player_id)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [PurchaseHistoryMapper.to_domain(o) for o in orms]

    async def get_purchase_count_today(
        self, player_id: UUID, shop_item_id: UUID, day: date
    ) -> int:
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        stmt = (
            select(func.count())
            .select_from(PurchaseHistoryORM)
            .where(PurchaseHistoryORM.player_id == player_id)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
            .where(PurchaseHistoryORM.purchased_at >= day_start)
            .where(PurchaseHistoryORM.purchased_at <= day_end)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_total_purchase_count(self, shop_item_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(PurchaseHistoryORM)
            .where(PurchaseHistoryORM.shop_item_id == shop_item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def save(self, history: PurchaseHistory) -> None:
        orm_obj = PurchaseHistoryMapper.to_orm(history)
        self.session.add(orm_obj)
