from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.domain.entities.item import Item
from app.domain.repositories.item_repository import ItemRepository
from app.infrastructure.persistence.models.item_orm import ItemORM
from app.infrastructure.persistence.mappers import ItemMapper

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