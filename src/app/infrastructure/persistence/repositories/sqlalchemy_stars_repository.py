from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.stars_package import StarsPackage
from app.domain.entities.transaction import Transaction, TransactionStatus
from app.domain.repositories.stars_repository import StarsPackageRepository, TransactionRepository
from app.infrastructure.persistence.mappers import StarsPackageMapper, TransactionMapper
from app.infrastructure.persistence.models.stars_package_orm import StarsPackageORM
from app.infrastructure.persistence.models.transaction_orm import TransactionORM

_STARS_SORT_WHITELIST = {"stars_amount", "xgen_reward"}


class SQLAlchemyStarsPackageRepository(StarsPackageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, package_id: UUID) -> StarsPackage | None:
        stmt = (
            select(StarsPackageORM)
            .where(StarsPackageORM.id == package_id)
            .where(StarsPackageORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return StarsPackageMapper.to_domain(orm) if orm else None

    async def get_all_active(self) -> list[StarsPackage]:
        stmt = (
            select(StarsPackageORM)
            .where(StarsPackageORM.is_active == True)
            .where(StarsPackageORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [StarsPackageMapper.to_domain(o) for o in orms]

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[StarsPackage], int]:
        base = select(StarsPackageORM).where(StarsPackageORM.deleted_at.is_(None))

        if search:
            base = base.where(StarsPackageORM.stars_amount.cast(func.text).ilike(f"%{search}%"))

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        if sort_by in _STARS_SORT_WHITELIST:
            column = getattr(StarsPackageORM, sort_by)
            base = base.order_by(column.desc() if sort_order == "desc" else column.asc())

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)

        result = await self.session.execute(base)
        orms = result.scalars().all()
        return [StarsPackageMapper.to_domain(o) for o in orms], total

    async def save(self, package: StarsPackage) -> None:
        orm_obj = StarsPackageMapper.to_orm(package)
        await self.session.merge(orm_obj)


class SQLAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_charge_id(self, telegram_charge_id: str) -> Transaction | None:
        stmt = select(TransactionORM).where(
            TransactionORM.telegram_charge_id == telegram_charge_id
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return TransactionMapper.to_domain(orm) if orm else None

    async def save(self, transaction: Transaction) -> None:
        orm_obj = TransactionMapper.to_orm(transaction)
        self.session.add(orm_obj)
