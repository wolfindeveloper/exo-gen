from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.uow import UnitOfWork
from app.domain.repositories.player_repository import PlayerRepository


@pytest.fixture
def mock_player_repo():
    repo = MagicMock(spec=PlayerRepository)
    repo.get_by_telegram_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


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
