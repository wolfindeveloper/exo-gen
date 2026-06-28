from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.equipment_repository import EquipmentRepository
from app.domain.entities.equipment import Equipment
from app.infrastructure.persistence.models.equipment_orm import EquipmentORM
from app.infrastructure.persistence.mappers import EquipmentMapper


class SQLAlchemyEquipmentRepository(EquipmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ship_id(self, ship_id: UUID) -> Equipment | None:
        stmt = select(EquipmentORM).where(EquipmentORM.ship_id == ship_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return EquipmentMapper.to_domain(orm) if orm else None

    async def save(self, equipment: Equipment) -> None:
        orm_obj = EquipmentMapper.to_orm(equipment)
        await self.session.merge(orm_obj)
