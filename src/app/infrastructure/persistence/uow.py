from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.uow import UnitOfWork
from app.domain.entities.base import AggregateRoot
from app.domain.events.dispatcher import dispatcher


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._aggregates: list[AggregateRoot] = []

    def track(self, *aggregates: AggregateRoot) -> None:
        self._aggregates.extend(aggregates)

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
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
