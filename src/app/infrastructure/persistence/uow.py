from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.uow import UnitOfWork
from app.domain.entities.base import AggregateRoot
from app.domain.events.dispatcher import dispatcher
from app.domain.repositories.purchase_repository import PurchaseRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.infrastructure.persistence.repositories.sqlalchemy_purchase_repository import SQLAlchemyPurchaseRepository
from app.infrastructure.persistence.repositories.sqlalchemy_inventory_repository import SQLAlchemyInventoryRepository
from app.infrastructure.persistence.repositories.sqlalchemy_shop_repository import SQLAlchemyShopItemRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._aggregates: list[AggregateRoot] = []
        self._purchases: PurchaseRepository | None = None
        self._inventory: InventoryRepository | None = None
        self._shop: ShopItemRepository | None = None

    @property
    def purchases(self) -> PurchaseRepository:
        if self._purchases is None:
            self._purchases = SQLAlchemyPurchaseRepository(self.session)
        return self._purchases

    @property
    def inventory(self) -> InventoryRepository:
        if self._inventory is None:
            self._inventory = SQLAlchemyInventoryRepository(self.session)
        return self._inventory

    @property
    def shop(self) -> ShopItemRepository:
        if self._shop is None:
            self._shop = SQLAlchemyShopItemRepository(self.session)
        return self._shop

    def track(self, *aggregates: AggregateRoot) -> None:
        self._aggregates.extend(aggregates)

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._purchases = SQLAlchemyPurchaseRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        events = []
        for agg in self._aggregates:
            events.extend(agg._events)
            agg._events.clear()
        self._aggregates.clear()

        await self.session.commit()

        for event in events:
            await dispatcher.dispatch(event)

    async def rollback(self) -> None:
        await self.session.rollback()
