"""Unit-тесты для expedition_service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from api.services.expedition_service import start_expedition
from core.models import Player, PlayerInventory, Ship


@pytest_asyncio.fixture
async def mock_db():
    """Моковая async-сессия SQLAlchemy."""
    db = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db


@pytest_asyncio.fixture
async def test_player():
    """Тестовый игрок."""
    return Player(
        id="player_test",
        telegram_id=999,
        username="TestPilot",
        level=1,
        xp=0,
        tier=1,
        xgen_balance=1000,
        verification_status="none",
        language="ru",
    )


@pytest_asyncio.fixture
async def test_ship(test_player):
    """Тестовый корабль T1."""
    return Ship(
        id=str(uuid.uuid4()),
        player_id=test_player.id,
        slug="seeker_dust_runner",
        stability=100,
        is_nft=False,
        is_staked=False,
        in_repair=False,
        repair_mode=None,
        repair_until=None,
        expedition_cycles=0,
    )


@pytest.mark.asyncio
async def test_start_expedition_validates_ship_ownership(mock_db, test_player, test_ship):
    """start_expedition() должен отклонять запрос, если игрок не владеет кораблём."""
    mock_db.get.return_value = test_player

    # Мокируем execute: возвращаем None (корабль не найден)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with patch("api.services.expedition_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "expeditions": {
                "expedition_scrap_run": {
                    "tier": 1,
                    "slug": "expedition_scrap_run",
                    "duration_hours": 4,
                    "xp_reward": 50,
                    "requires_verification": None,
                }
            },
            "ships": {
                "seeker_dust_runner": {"tier": 1, "slug": "seeker_dust_runner"},
            },
        }[name]

        with pytest.raises(ValueError, match="Player does not own ship"):
            await start_expedition(
                player_id="player_test",
                ship_slug="vanguard_nebula_ghost",  # Другой корабль
                tier=1,
                fuel_slug="fuel_t1_mangan_hydride",
                overdrive_mode="stable",
                db=mock_db,
            )


@pytest.mark.asyncio
async def test_start_expedition_validates_fuel_balance(mock_db, test_player, test_ship):
    """start_expedition() должен отклонять запрос при отсутствии топлива."""
    mock_db.get.return_value = test_player

    # Корабль найден
    ship_result = MagicMock()
    ship_result.scalar_one_or_none.return_value = test_ship

    # Топливо не найдено (quantity < 1)
    fuel_result = MagicMock()
    fuel_result.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [ship_result, fuel_result]

    with patch("api.services.expedition_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "expeditions": {
                "expedition_scrap_run": {
                    "tier": 1,
                    "slug": "expedition_scrap_run",
                    "duration_hours": 4,
                    "xp_reward": 50,
                    "requires_verification": None,
                }
            },
            "ships": {
                "seeker_dust_runner": {"tier": 1, "slug": "seeker_dust_runner"},
            },
        }[name]

        with pytest.raises(ValueError, match="Insufficient fuel"):
            await start_expedition(
                player_id="player_test",
                ship_slug="seeker_dust_runner",
                tier=1,
                fuel_slug="fuel_t1_mangan_hydride",
                overdrive_mode="stable",
                db=mock_db,
            )


@pytest.mark.asyncio
async def test_start_expedition_validates_tier_access(mock_db, test_player):
    """start_expedition() должен отклонять экспедиции выше тира игрока."""
    mock_db.get.return_value = test_player

    with patch("api.services.expedition_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "expeditions": {
                "expedition_genesis_point": {
                    "tier": 5,
                    "slug": "expedition_genesis_point",
                    "duration_hours": 24,
                    "xp_reward": 1000,
                    "requires_verification": "VERIFIED",
                }
            },
            "ships": {
                "seeker_dust_runner": {"tier": 1, "slug": "seeker_dust_runner"},
            },
        }[name]

        # Тир 5 требует VERIFIED статус, у игрока "none"
        with pytest.raises(PermissionError, match="VERIFIED status"):
            await start_expedition(
                player_id="player_test",
                ship_slug="seeker_dust_runner",
                tier=5,
                fuel_slug="fuel_t5_dark_matter",
                overdrive_mode="stable",
                db=mock_db,
            )


@pytest.mark.asyncio
async def test_start_expedition_rejects_staked_ship(mock_db, test_player, test_ship):
    """start_expedition() должен отклонять стейкнутые корабли."""
    test_ship.is_staked = True
    mock_db.get.return_value = test_player

    ship_result = MagicMock()
    ship_result.scalar_one_or_none.return_value = test_ship
    mock_db.execute.return_value = ship_result

    with patch("api.services.expedition_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "expeditions": {
                "expedition_scrap_run": {
                    "tier": 1,
                    "slug": "expedition_scrap_run",
                    "duration_hours": 4,
                    "xp_reward": 50,
                    "requires_verification": None,
                }
            },
            "ships": {
                "seeker_dust_runner": {"tier": 1, "slug": "seeker_dust_runner"},
            },
        }[name]

        with pytest.raises(ValueError, match="Staked ships cannot go on expeditions"):
            await start_expedition(
                player_id="player_test",
                ship_slug="seeker_dust_runner",
                tier=1,
                fuel_slug="fuel_t1_mangan_hydride",
                overdrive_mode="stable",
                db=mock_db,
            )


@pytest.mark.asyncio
async def test_start_expedition_rejects_ship_in_repair(mock_db, test_player, test_ship):
    """start_expedition() должен отклонять корабли в ремонте."""
    test_ship.in_repair = True
    mock_db.get.return_value = test_player

    ship_result = MagicMock()
    ship_result.scalar_one_or_none.return_value = test_ship
    mock_db.execute.return_value = ship_result

    with patch("api.services.expedition_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "expeditions": {
                "expedition_scrap_run": {
                    "tier": 1,
                    "slug": "expedition_scrap_run",
                    "duration_hours": 4,
                    "xp_reward": 50,
                    "requires_verification": None,
                }
            },
            "ships": {
                "seeker_dust_runner": {"tier": 1, "slug": "seeker_dust_runner"},
            },
        }[name]

        with pytest.raises(ValueError, match="Ship is currently under repair"):
            await start_expedition(
                player_id="player_test",
                ship_slug="seeker_dust_runner",
                tier=1,
                fuel_slug="fuel_t1_mangan_hydride",
                overdrive_mode="stable",
                db=mock_db,
            )
