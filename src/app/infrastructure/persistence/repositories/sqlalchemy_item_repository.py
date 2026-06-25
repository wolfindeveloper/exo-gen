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
        # merge() в SQLAlchemy — это умный метод. 
        # Если предмета с таким ID нет в БД, он сделает INSERT.
        # Если есть и он изменился — сделает UPDATE.
        await self.session.merge(orm_obj)
        await self.session.commit()

    async def get_by_id(self, item_id: UUID) -> Item | None:
        stmt = select(ItemORM).where(ItemORM.id == item_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return ItemMapper.to_domain(orm) if orm else None

    async def get_all(self) -> list[Item]:
        stmt = select(ItemORM)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ItemMapper.to_domain(o) for o in orms]