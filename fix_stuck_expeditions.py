import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.app.config.settings import settings
from src.app.infrastructure.persistence.repositories.sqlalchemy_expedition_repository import (
    SQLAlchemyExpeditionRepository,
)
from src.app.infrastructure.persistence.repositories.sqlalchemy_player_repository import (
    SQLAlchemyPlayerRepository,
)
from src.app.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from src.app.application.use_cases.process_finished_expeditions import (
    ProcessFinishedExpeditionsUseCase,
)


async def main():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    async with session_factory() as session:
        expedition_repo = SQLAlchemyExpeditionRepository(session)
        player_repo = SQLAlchemyPlayerRepository(session)
        uow = SQLAlchemyUnitOfWork(session)

        use_case = ProcessFinishedExpeditionsUseCase(
            expedition_repo=expedition_repo,
            player_repo=player_repo,
        )

        count = await use_case.execute(uow)

    await engine.dispose()

    if count > 0:
        print(f"Обработано зависших экспедиций: {count}")
    else:
        print("Зависших экспедиций не найдено.")


if __name__ == "__main__":
    asyncio.run(main())
