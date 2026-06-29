from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

import pytest

from app.application.use_cases.unlock_article import UnlockArticleUseCase
from app.application.use_cases.get_guide import GetGuideUseCase
from app.domain.entities.player import Player
from app.domain.entities.chapter import Chapter
from app.domain.entities.article import Article
from app.domain.entities.season import Season
from app.domain.value_objects.resources import XgenBalance, FragmentsBalance
from app.domain.exceptions.guide import SeasonExpiredError
from app.domain.repositories.season_repository import SeasonRepository


TG_ID = 12345
PLAYER_USERNAME = "arthur"


def make_player(player_id):
    return Player(
        id=player_id,
        telegram_id=TG_ID,
        username=PLAYER_USERNAME,
        xp=0,
        xgen_balance=XgenBalance(0),
        fragments_balance=FragmentsBalance(100),
        daily_streak=0,
        last_login_date=None,
        ships=[],
    )


def make_active_season(season_id):
    return Season(
        id=season_id,
        name="Active Season",
        description="Currently active",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) + timedelta(days=10),
        is_active=True,
    )


def make_expired_season(season_id):
    return Season(
        id=season_id,
        name="Expired Season",
        description="Already ended",
        start_date=datetime.now(timezone.utc) - timedelta(days=20),
        end_date=datetime.now(timezone.utc) - timedelta(days=10),
        is_active=True,
    )


def make_chapter(chapter_id, article, season_id=None):
    article.chapter_id = chapter_id
    return Chapter(
        id=chapter_id,
        name="Test Chapter",
        description="A chapter",
        is_secret=False,
        season_id=season_id,
        reward_xgen=10,
        reward_fragments=5,
        articles=[article],
    )


def make_article(article_id):
    return Article(
        id=article_id,
        chapter_id=uuid4(),
        title="Test Article",
        content="Test content",
        fragment_cost=10,
    )


@pytest.fixture
def mock_season_repo():
    repo = MagicMock(spec=SeasonRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_chapter_repo():
    repo = MagicMock()
    repo.get_chapter_by_article_id = AsyncMock()
    repo.get_all_with_articles = AsyncMock()
    return repo


@pytest.fixture
def mock_guide_repo():
    repo = MagicMock()
    repo.is_article_unlocked = AsyncMock(return_value=False)
    repo.get_unlocked_articles_ids = AsyncMock(return_value=set())
    repo.is_chapter_completed = AsyncMock(return_value=False)
    repo.save_unlocked_article = AsyncMock()
    repo.save_chapter_completion = AsyncMock()
    return repo


@pytest.fixture
def mock_loot_box_service():
    return MagicMock()


class TestUnlockArticleSeasonValidation:
    @pytest.mark.asyncio
    async def test_unlock_article_season_expired(
        self, mock_player_repo, mock_chapter_repo, mock_guide_repo,
        mock_inventory_repo, mock_loot_box_repo, mock_loot_box_service,
        mock_season_repo, mock_uow, player_id
    ):
        article_id = uuid4()
        chapter_id = uuid4()
        season_id = uuid4()

        player = make_player(player_id)
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article, season_id=season_id)

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_season_repo.get_by_id.return_value = make_expired_season(season_id)

        use_case = UnlockArticleUseCase(
            mock_player_repo,
            mock_chapter_repo,
            mock_season_repo,
            mock_guide_repo,
            loot_box_service=mock_loot_box_service,
            loot_box_repo=mock_loot_box_repo,
            inventory_repo=mock_inventory_repo,
        )

        with pytest.raises(SeasonExpiredError, match="Expired Season"):
            await use_case.execute(player, article_id, mock_uow)

        mock_player_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_unlock_article_active_season_succeeds(
        self, mock_player_repo, mock_chapter_repo, mock_guide_repo,
        mock_inventory_repo, mock_loot_box_repo, mock_loot_box_service,
        mock_season_repo, mock_uow, player_id
    ):
        article_id = uuid4()
        chapter_id = uuid4()
        season_id = uuid4()

        player = make_player(player_id)
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article, season_id=season_id)

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_season_repo.get_by_id.return_value = make_active_season(season_id)

        use_case = UnlockArticleUseCase(
            mock_player_repo,
            mock_chapter_repo,
            mock_season_repo,
            mock_guide_repo,
            loot_box_service=mock_loot_box_service,
            loot_box_repo=mock_loot_box_repo,
            inventory_repo=mock_inventory_repo,
        )

        result = await use_case.execute(player, article_id, mock_uow)

        assert result is not None
        mock_player_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()


class TestGetGuideSeasonFilter:
    @pytest.mark.asyncio
    async def test_get_guide_filters_expired_seasonal_chapters(
        self, mock_season_repo, player_id
    ):
        season_id = uuid4()
        chapter_id = uuid4()
        article_id = uuid4()

        player = make_player(player_id)
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article, season_id=season_id)

        chapter_repo = MagicMock()
        chapter_repo.get_all_with_articles = AsyncMock(return_value=[chapter])

        mock_season_repo.get_by_id.return_value = make_expired_season(season_id)

        progress_repo = MagicMock()
        progress_repo.get_unlocked_articles_ids = AsyncMock(return_value=set())
        progress_repo.is_chapter_completed = AsyncMock(return_value=False)

        use_case = GetGuideUseCase(chapter_repo, mock_season_repo, progress_repo)
        result = await use_case.execute(player)

        assert len(result.chapters) == 0

    @pytest.mark.asyncio
    async def test_get_guide_keeps_completed_expired_chapters(
        self, mock_season_repo, player_id
    ):
        season_id = uuid4()
        chapter_id = uuid4()
        article_id = uuid4()

        player = make_player(player_id)
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article, season_id=season_id)

        chapter_repo = MagicMock()
        chapter_repo.get_all_with_articles = AsyncMock(return_value=[chapter])

        mock_season_repo.get_by_id.return_value = make_expired_season(season_id)

        progress_repo = MagicMock()
        progress_repo.get_unlocked_articles_ids = AsyncMock(return_value={article_id})
        progress_repo.is_chapter_completed = AsyncMock(return_value=True)

        use_case = GetGuideUseCase(chapter_repo, mock_season_repo, progress_repo)
        result = await use_case.execute(player)

        assert len(result.chapters) == 1
        assert result.chapters[0].id == chapter_id
