"""Async fixtures для интеграционных и unit-тестов."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.main import app
from core.database import get_db
from core.models import Base
from core.redis import get_redis


# Тестовый engine (session-scoped)
test_engine = create_async_engine(
    "postgresql+asyncpg://dev:devpassword@localhost:5434/exogenesis",
    echo=False,
    pool_pre_ping=True,
)

TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Создаёт таблицы один раз на всю сессию тестов."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(setup_test_db) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP-клиент для тестирования API эндпоинтов."""

    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Мокируем Redis для тестов
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 0
    mock_redis.keys.return_value = []

    async def override_get_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def mock_telegram_user(user_id: int = 123, username: str = "TestNavigator") -> str:
    """Генерирует моковый заголовок X-Telegram-User."""
    user_data = {
        "id": user_id,
        "username": username,
        "first_name": "Test",
        "last_name": "User",
    }
    return json.dumps(user_data, ensure_ascii=False)


@pytest.fixture
def mock_ton_client():
    """Мокирует все вызовы к TON блокчейну."""
    with patch("blockchain.ton_client.TonClient") as mock:
        instance = AsyncMock()
        instance.get_balance.return_value = "1000000000"
        instance.mint_nft.return_value = {"tx_hash": "mock_tx_hash", "nft_address": "mock_address"}
        instance.mint_sbt.return_value = {"tx_hash": "mock_tx_hash", "sbt_address": "mock_address"}
        instance.send_transaction.return_value = {"tx_hash": "mock_tx_hash"}
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_telegram_auth():
    """Мокирует валидацию Telegram initData."""
    with patch("api.middleware.auth.validate_telegram_init_data") as mock:
        mock.return_value = {"id": 123, "username": "TestNavigator"}
        yield mock
