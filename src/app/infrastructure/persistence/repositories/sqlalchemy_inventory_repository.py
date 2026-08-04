from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from uuid import UUID, uuid4

from app.domain.entities.inventory import Inventory
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.persistence.models.inventory_item_orm import InventoryItemORM
from app.infrastructure.persistence.mappers import InventoryMapper, InventoryItemMapper

class SQLAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_item_id(self, item_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(InventoryItemORM)
            .where(InventoryItemORM.item_id == item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_player_id(self, player_id: UUID, for_update: bool = False) -> Inventory:
        stmt = select(InventoryItemORM).where(InventoryItemORM.player_id == player_id)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        items_orm = result.scalars().all()
        
        return InventoryMapper.to_domain(player_id, items_orm)

    async def add_item_quantity(self, player_id: UUID, item_id: UUID, quantity: int) -> None:
        stmt = (
            insert(InventoryItemORM)
            .values(
                id=uuid4(),
                player_id=player_id,
                item_id=item_id,
                quantity=quantity,
                item_metadata={},
            )
            .on_conflict_do_update(
                index_elements=["player_id", "item_id"],
                set_=dict(
                    quantity=InventoryItemORM.quantity + quantity,
                ),
            )
        )
        await self.session.execute(stmt)

    async def save(self, inventory: Inventory) -> None:
        try:
            with self.session.no_autoflush:
                stmt = select(InventoryItemORM).where(InventoryItemORM.player_id == inventory.player_id)
                result = await self.session.execute(stmt)
                existing_items_orm = {item.item_id: item for item in result.scalars().all()}

            for domain_item in inventory.items:
                if domain_item.item_id in existing_items_orm:
                    orm_item = existing_items_orm.pop(domain_item.item_id)
                    orm_item.quantity = domain_item.quantity
                    orm_item.item_metadata = domain_item.metadata
                else:
                    new_orm = InventoryItemMapper.to_orm(domain_item)
                    self.session.add(new_orm)

            for orphan_orm in existing_items_orm.values():
                await self.session.delete(orphan_orm)

        except IntegrityError as e:
            if "uq_inventory_player_item" in str(e):
                await self.session.rollback()
                fresh_inventory = await self.get_by_player_id(inventory.player_id, for_update=True)
                for domain_item in inventory.items:
                    fresh_inventory.add_item(domain_item.item_id, domain_item.quantity)
                return await self.save(fresh_inventory)
            raise