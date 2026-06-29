from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.repositories.item_repository import ItemRepository
from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService


@pytest.fixture
def mock_player_repo():
    repo = MagicMock(spec=PlayerRepository)
    repo.get_by_telegram_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_inventory_repo():
    repo = MagicMock(spec=InventoryRepository)
    repo.get_by_player_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_item_repo():
    repo = MagicMock(spec=ItemRepository)
    repo.get_by_ids = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_loot_box_repo():
    repo = MagicMock(spec=LootBoxRepository)
    repo.get_by_type = AsyncMock()
    repo.save = AsyncMock()
    repo.get_all = AsyncMock()
    return repo


@pytest.fixture
def mock_loot_box_service():
    return MagicMock(spec=LootBoxService)


@pytest.fixture
def mock_uow():
    uow = MagicMock(spec=UnitOfWork)
    uow.track = MagicMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def player_id():
    return uuid4()
