from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import AsyncSessionLocal
from app.domain.repositories.player_repository import PlayerRepository
from app.infrastructure.persistence.repositories.sqlalchemy_player_repository import SQLAlchemyPlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.infrastructure.persistence.repositories.sqlalchemy_zone_repository import SQLAlchemyZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.infrastructure.persistence.repositories.sqlalchemy_expedition_repository import SQLAlchemyExpeditionRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.infrastructure.persistence.repositories.sqlalchemy_chapter_repository import SQLAlchemyChapterRepository
from app.infrastructure.persistence.repositories.sqlalchemy_guide_progress_repository import SQLAlchemyGuideProgressRepository
from app.domain.repositories.item_repository import ItemRepository
from app.infrastructure.persistence.repositories.sqlalchemy_item_repository import SQLAlchemyItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.persistence.repositories.sqlalchemy_inventory_repository import SQLAlchemyInventoryRepository

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_player_repo(session: AsyncSession = Depends(get_db_session)) -> PlayerRepository:
    return SQLAlchemyPlayerRepository(session)

async def get_zone_repo(session: AsyncSession = Depends(get_db_session)) -> ZoneRepository:
    return SQLAlchemyZoneRepository(session)

async def get_expedition_repo(session: AsyncSession = Depends(get_db_session)) -> ExpeditionRepository:
    return SQLAlchemyExpeditionRepository(session)

async def get_chapter_repo(session: AsyncSession = Depends(get_db_session)) -> ChapterRepository:
    return SQLAlchemyChapterRepository(session)

async def get_guide_progress_repo(session: AsyncSession = Depends(get_db_session)) -> GuideProgressRepository:
    return SQLAlchemyGuideProgressRepository(session)

async def get_item_repo(session: AsyncSession = Depends(get_db_session)) -> ItemRepository:
    return SQLAlchemyItemRepository(session)

async def get_inventory_repo(session: AsyncSession = Depends(get_db_session)) -> InventoryRepository:
    return SQLAlchemyInventoryRepository(session)