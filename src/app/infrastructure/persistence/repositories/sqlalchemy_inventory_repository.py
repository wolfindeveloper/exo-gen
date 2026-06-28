from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.domain.entities.inventory import Inventory
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.persistence.models.inventory_item_orm import InventoryItemORM
from app.infrastructure.persistence.mappers import InventoryMapper, InventoryItemMapper

class SQLAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_player_id(self, player_id: UUID) -> Inventory:
        stmt = select(InventoryItemORM).where(InventoryItemORM.player_id == player_id)
        result = await self.session.execute(stmt)
        items_orm = result.scalars().all()
        
        # Если у игрока еще нет предметов, вернется пустой список, 
        # и InventoryMapper создаст пустой Агрегат.
        return InventoryMapper.to_domain(player_id, items_orm)

    async def save(self, inventory: Inventory) -> None:
        stmt = select(InventoryItemORM).where(InventoryItemORM.player_id == inventory.player_id)
        result = await self.session.execute(stmt)
        existing_items_orm = {item.id: item for item in result.scalars().all()}

        for domain_item in inventory.items:
            if domain_item.id in existing_items_orm:
                orm_item = existing_items_orm[domain_item.id]
                orm_item.quantity = domain_item.quantity
                orm_item.item_metadata = domain_item.metadata
            else:
                new_orm = InventoryItemMapper.to_orm(domain_item)
                self.session.add(new_orm)