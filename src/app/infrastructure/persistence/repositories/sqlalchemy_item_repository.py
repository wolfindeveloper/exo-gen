from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository
from app.infrastructure.persistence.models.item_orm import ItemORM
from app.infrastructure.persistence.mappers import ItemMapper

_ITEM_SORT_WHITELIST = {"name", "type", "rarity", "sell_price"}


class SQLAlchemyItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, item: Item) -> None:
        orm_obj = ItemMapper.to_orm(item)
        await self.session.merge(orm_obj)

    async def get_by_id(self, item_id: UUID) -> Item | None:
        stmt = (
            select(ItemORM)
            .where(ItemORM.id == item_id)
            .where(ItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return ItemMapper.to_domain(orm) if orm else None

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Item], int]:
        base = select(ItemORM).where(ItemORM.deleted_at.is_(None))

        if search:
            base = base.where(ItemORM.name.ilike(f"%{search}%"))

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        if sort_by in _ITEM_SORT_WHITELIST:
            column = getattr(ItemORM, sort_by)
            base = base.order_by(column.desc() if sort_order == "desc" else column.asc())

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)

        result = await self.session.execute(base)
        orms = result.scalars().all()
        return [ItemMapper.to_domain(o) for o in orms], total

    async def get_all(self) -> list[Item]:
        stmt = select(ItemORM).where(ItemORM.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ItemMapper.to_domain(o) for o in orms]

    async def get_by_ids(self, item_ids: list[UUID]) -> list[Item]:
        stmt = (
            select(ItemORM)
            .where(ItemORM.id.in_(item_ids))
            .where(ItemORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ItemMapper.to_domain(o) for o in orms]

    async def get_consumables_with_effect(self, effect_key: str) -> list[Item]:
        from app.domain.entities.item import ItemType
        stmt = (
            select(ItemORM)
            .where(ItemORM.deleted_at.is_(None))
            .where(ItemORM.type == ItemType.CONSUMABLE.value)
            .where(ItemORM.effect.has_key(effect_key))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ItemMapper.to_domain(o) for o in orms]