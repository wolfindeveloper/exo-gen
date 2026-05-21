"""Unit-тесты для laboratory_service."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from api.services.laboratory_service import (
    _generate_recipe_hash,
    attempt_craft,
)
from core.models import Artifact, Player, PlayerInventory


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
    """Тестовый игрок с балансом."""
    return Player(
        id="player_test",
        telegram_id=999,
        username="TestAlchemist",
        level=5,
        xp=500,
        tier=2,
        xgen_balance=500,
        verification_status="none",
        language="ru",
    )


@pytest.mark.asyncio
async def test_generate_recipe_hash_deterministic():
    """SHA-256 хэш должен быть детерминированным: одинаковые входы → одинаковый хэш."""
    essences = ["essence_t2", "essence_t1", "essence_t3"]
    domain = "zone_inner_rim"
    xgen = 100

    hash1 = _generate_recipe_hash(essences, domain, xgen)
    hash2 = _generate_recipe_hash(essences, domain, xgen)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 = 64 hex chars


@pytest.mark.asyncio
async def test_generate_recipe_hash_order_independent():
    """Порядок эссенций не должен влиять на хэш (sorted)."""
    essences_a = ["essence_t1", "essence_t2", "essence_t3"]
    essences_b = ["essence_t3", "essence_t1", "essence_t2"]

    hash_a = _generate_recipe_hash(essences_a, "zone_inner_rim", 100)
    hash_b = _generate_recipe_hash(essences_b, "zone_inner_rim", 100)

    assert hash_a == hash_b


@pytest.mark.asyncio
async def test_generate_recipe_hash_different_inputs():
    """Разные входы должны давать разные хэши."""
    hash1 = _generate_recipe_hash(["essence_t1"], "zone_inner_rim", 100)
    hash2 = _generate_recipe_hash(["essence_t2"], "zone_inner_rim", 100)
    hash3 = _generate_recipe_hash(["essence_t1"], "zone_nebula_belt", 100)
    hash4 = _generate_recipe_hash(["essence_t1"], "zone_inner_rim", 200)

    assert hash1 != hash2
    assert hash1 != hash3
    assert hash1 != hash4


@pytest.mark.asyncio
async def test_attempt_craft_first_craft_creates_artifact(mock_db, test_player):
    """Первый крафт с уникальным хэшем должен создавать артефакт."""
    mock_db.get.return_value = test_player

    # Инвентарь: эссенции есть (3 проверки + 3 consume)
    inv_result = MagicMock()
    inv_item = PlayerInventory(
        id=str(uuid.uuid4()),
        player_id="player_test",
        slug="essence_t1",
        quantity=5,
    )
    inv_result.scalar_one_or_none.return_value = inv_item

    # Артефакт с таким хэшем не найден
    artifact_result = MagicMock()
    artifact_result.scalar_one_or_none.return_value = None

    # Нужно 7 вызовов: 3 has_inventory + 1 find_artifact + 3 consume_inventory
    mock_db.execute.side_effect = [
        inv_result, inv_result, inv_result,  # has_inventory x3
        artifact_result,                      # find_artifact
        inv_result, inv_result, inv_result,   # consume_inventory x3
    ]

    with patch("api.services.laboratory_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "lab_rules": {
                "lab_rules": {
                    "min_essences": 3,
                    "max_essences": 5,
                    "failure_return_percent": 50,
                },
                "essence_tiers": {},
            },
            "galaxy_zones": {
                "galaxy_zones": {
                    "zone_inner_rim": {
                        "tier": 1,
                        "slug": "zone_inner_rim",
                    }
                }
            },
            "artifact_erosion": {
                "artifact_erosion": {
                    "default_cycles": 10,
                    "floor_percent": 10,
                    "calibration_cost": {"xgen": 25, "resource_slug": "essence_t2"},
                },
                "staking_yield": {},
            },
        }[name]

        result = await attempt_craft(
            player_id="player_test",
            domain_slug="zone_inner_rim",
            essences=["essence_t1", "essence_t2", "essence_t3"],
            xgen_amount=100,
            db=mock_db,
        )

        assert result["status"] == "created"
        assert result["artifact_id"] is not None
        assert result["recipe_hash"] is not None
        assert result["xgen_burned"] == 100


@pytest.mark.asyncio
async def test_attempt_craft_duplicate_hash_returns_taken(mock_db, test_player):
    """Второй крафт с тем же хэшем должен возвращать status='taken'."""
    mock_db.get.return_value = test_player

    # Инвентарь: эссенции есть (3 проверки + 3 add для refund)
    inv_result = MagicMock()
    inv_item = PlayerInventory(
        id=str(uuid.uuid4()),
        player_id="player_test",
        slug="essence_t1",
        quantity=5,
    )
    inv_result.scalar_one_or_none.return_value = inv_item

    # Артефакт с таким хэшем уже существует
    existing_artifact = Artifact(
        id=str(uuid.uuid4()),
        player_id="player_other",
        slug="artifact_existing",
        recipe_hash="existing_hash",
        status="active",
        cycles_remaining=10,
        domain_slug="zone_inner_rim",
        bonus_multiplier=1.0,
        accumulated_yield=0.0,
    )
    artifact_result = MagicMock()
    artifact_result.scalar_one_or_none.return_value = existing_artifact

    # Нужно 7 вызовов: 3 has_inventory + 1 find_artifact + 3 add_inventory (refund)
    mock_db.execute.side_effect = [
        inv_result, inv_result, inv_result,  # has_inventory x3
        artifact_result,                      # find_artifact
        inv_result, inv_result, inv_result,   # add_inventory x3 (refund)
    ]

    with patch("api.services.laboratory_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "lab_rules": {
                "lab_rules": {
                    "min_essences": 3,
                    "max_essences": 5,
                    "failure_return_percent": 50,
                },
                "essence_tiers": {},
            },
            "galaxy_zones": {
                "galaxy_zones": {
                    "zone_inner_rim": {
                        "tier": 1,
                        "slug": "zone_inner_rim",
                    }
                }
            },
            "artifact_erosion": {
                "artifact_erosion": {
                    "default_cycles": 10,
                    "floor_percent": 10,
                    "calibration_cost": {"xgen": 25, "resource_slug": "essence_t2"},
                },
                "staking_yield": {},
            },
        }[name]

        # Мокируем _generate_recipe_hash чтобы вернуть существующий хэш
        with patch(
            "api.services.laboratory_service._generate_recipe_hash",
            return_value="existing_hash",
        ):
            result = await attempt_craft(
                player_id="player_test",
                domain_slug="zone_inner_rim",
                essences=["essence_t1", "essence_t2", "essence_t3"],
                xgen_amount=100,
                db=mock_db,
            )

            assert result["status"] == "taken"
            assert result["artifact_id"] is None
            assert result["xgen_burned"] == 100
            assert result["essences_refunded"] is not None


@pytest.mark.asyncio
async def test_attempt_craft_validates_min_essences(mock_db, test_player):
    """Крафт должен отклонять менее min_essences."""
    mock_db.get.return_value = test_player

    with patch("api.services.laboratory_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "lab_rules": {
                "lab_rules": {
                    "min_essences": 3,
                    "max_essences": 5,
                    "failure_return_percent": 50,
                },
                "essence_tiers": {},
            },
            "galaxy_zones": {
                "galaxy_zones": {
                    "zone_inner_rim": {"tier": 1, "slug": "zone_inner_rim"},
                }
            },
        }[name]

        with pytest.raises(ValueError, match="Minimum 3 essences required"):
            await attempt_craft(
                player_id="player_test",
                domain_slug="zone_inner_rim",
                essences=["essence_t1"],  # Только 1 эссенция
                xgen_amount=100,
                db=mock_db,
            )


@pytest.mark.asyncio
async def test_attempt_craft_validates_xgen_balance(mock_db, test_player):
    """Крафт должен отклонять при недостатке XGEN."""
    test_player.xgen_balance = 50  # Меньше чем нужно
    mock_db.get.return_value = test_player

    with patch("api.services.laboratory_service.load_config") as mock_load:
        mock_load.side_effect = lambda name: {
            "lab_rules": {
                "lab_rules": {
                    "min_essences": 3,
                    "max_essences": 5,
                    "failure_return_percent": 50,
                },
                "essence_tiers": {},
            },
            "galaxy_zones": {
                "galaxy_zones": {
                    "zone_inner_rim": {"tier": 1, "slug": "zone_inner_rim"},
                }
            },
        }[name]

        with pytest.raises(ValueError, match="Insufficient"):
            await attempt_craft(
                player_id="player_test",
                domain_slug="zone_inner_rim",
                essences=["essence_t1", "essence_t2", "essence_t3"],
                xgen_amount=100,  # Нужно 100, есть 50
                db=mock_db,
            )
