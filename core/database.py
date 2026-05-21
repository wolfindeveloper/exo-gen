"""Async SQLAlchemy engine and session management."""

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """FastAPI dependency yielding an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def test_connection() -> bool:
    """Verify database connectivity with a lightweight query."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def init_db() -> None:
    """Create all tables if they don't exist.

    DEV ONLY — production should use Alembic migrations.
    Base.metadata.create_all is safe: it only creates missing tables.
    """
    from core.models import Base

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized")
    except Exception as exc:
        logger.error("❌ Failed to initialize database tables: %s", exc)
        raise


async def close_engine() -> None:
    """Dispose the engine pool on shutdown."""
    await engine.dispose()
