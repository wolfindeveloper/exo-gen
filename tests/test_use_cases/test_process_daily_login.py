from datetime import date, datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest

from app.application.use_cases.process_daily_login import ProcessDailyLoginUseCase
from app.domain.entities.player import Player
from app.domain.exceptions.player import PlayerNotFoundError
from app.domain.services.clock import Clock
from app.domain.value_objects.resources import XgenBalance, FragmentsBalance


TG_ID = 12345
PLAYER_USERNAME = "arthur"


def make_player(
    player_id,
    xp=0,
    xgen=0,
    fragments=0,
    streak=0,
    last_login=None,
    ships=None,
):
    return Player(
        id=player_id,
        telegram_id=TG_ID,
        username=PLAYER_USERNAME,
        xp=xp,
        xgen_balance=XgenBalance(xgen),
        fragments_balance=FragmentsBalance(fragments),
        daily_streak=streak,
        last_login_date=last_login,
        ships=ships or [],
    )


def make_clock(today: date, now: datetime | None = None) -> MagicMock:
    clock = MagicMock(spec=Clock)
    clock.today.return_value = today
    clock.now.return_value = now or datetime.now(timezone.utc)
    return clock


TODAY = date.today()


class TestProcessDailyLogin:
    @pytest.mark.asyncio
    async def test_first_login_sets_streak_to_1_and_grants_10_xp(
        self, mock_player_repo, mock_uow, player_id
    ):
        player = make_player(player_id)
        mock_player_repo.get_by_telegram_id.return_value = player
        use_case = ProcessDailyLoginUseCase(mock_player_repo)

        result = await use_case.execute(TG_ID, mock_uow)

        assert result.earned_xp == 10
        assert result.new_streak == 1
        assert result.got_box is False
        assert result.already_claimed is False

        assert player.xp == 10
        assert player.daily_streak == 1
        assert player.last_login_date == TODAY

        mock_player_repo.save.assert_awaited_once_with(player)
        mock_uow.track.assert_called_once_with(player)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_double_login_same_day_returns_already_claimed(
        self, mock_player_repo, mock_uow, player_id
    ):
        player = make_player(player_id, xp=50, streak=5, last_login=TODAY)
        mock_player_repo.get_by_telegram_id.return_value = player
        use_case = ProcessDailyLoginUseCase(mock_player_repo)

        result = await use_case.execute(TG_ID, mock_uow)

        assert result.earned_xp == 0
        assert result.new_streak == 5
        assert result.got_box is False
        assert result.already_claimed is True

        assert player.xp == 50
        assert player.daily_streak == 5

        mock_player_repo.save.assert_awaited_once_with(player)
        mock_uow.track.assert_called_once_with(player)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_login_after_skip_resets_streak_to_1(
        self, mock_player_repo, mock_uow, player_id
    ):
        old_date = TODAY - timedelta(days=3)
        player = make_player(player_id, xp=30, streak=3, last_login=old_date)
        mock_player_repo.get_by_telegram_id.return_value = player
        use_case = ProcessDailyLoginUseCase(mock_player_repo)

        result = await use_case.execute(TG_ID, mock_uow)

        assert result.earned_xp == 10
        assert result.new_streak == 1
        assert result.already_claimed is False

        assert player.xp == 40
        assert player.daily_streak == 1
        assert player.last_login_date == TODAY

        mock_player_repo.save.assert_awaited_once_with(player)
        mock_uow.track.assert_called_once_with(player)
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_player_not_found_raises_error(
        self, mock_player_repo, mock_uow, player_id
    ):
        mock_player_repo.get_by_telegram_id.return_value = None
        use_case = ProcessDailyLoginUseCase(mock_player_repo)

        with pytest.raises(PlayerNotFoundError):
            await use_case.execute(TG_ID, mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()
