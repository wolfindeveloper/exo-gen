from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.stars_package import StarsPackage
from app.domain.entities.transaction import Transaction, TransactionStatus
from app.domain.repositories.stars_repository import StarsPackageRepository, TransactionRepository
from app.infrastructure.persistence.mappers import StarsPackageMapper, TransactionMapper
from app.infrastructure.persistence.models.stars_package_orm import StarsPackageORM
from app.infrastructure.persistence.models.transaction_orm import TransactionORM


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
