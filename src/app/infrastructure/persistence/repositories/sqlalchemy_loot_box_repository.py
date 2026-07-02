from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.loot_box_config import LootBoxConfig
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.infrastructure.persistence.mappers import LootBoxMapper
from app.infrastructure.persistence.models.loot_box_config_orm import LootBoxConfigORM


class SQLAlchemyLootBoxRepository(LootBoxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, config_id: UUID) -> LootBoxConfig | None:
        stmt = (
            select(LootBoxConfigORM)
            .where(LootBoxConfigORM.id == config_id)
            .where(LootBoxConfigORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return LootBoxMapper.to_domain(orm) if orm else None

    async def get_by_type(self, box_type: str) -> LootBoxConfig | None:
        stmt = (
            select(LootBoxConfigORM)
            .where(LootBoxConfigORM.box_type == box_type)
            .where(LootBoxConfigORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return LootBoxMapper.to_domain(orm) if orm else None

    async def save(self, config: LootBoxConfig) -> None:
        orm_obj = LootBoxMapper.to_orm(config)
        await self.session.merge(orm_obj)

    async def get_all(self) -> list[LootBoxConfig]:
        stmt = select(LootBoxConfigORM).where(LootBoxConfigORM.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [LootBoxMapper.to_domain(o) for o in orms]
