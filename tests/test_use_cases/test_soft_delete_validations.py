from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

import pytest

from app.application.use_cases.soft_delete_season import SoftDeleteSeasonUseCase
from app.application.use_cases.soft_delete_article import SoftDeleteArticleUseCase
from app.application.use_cases.soft_delete_zone import SoftDeleteZoneUseCase
from app.application.use_cases.soft_delete_item import SoftDeleteItemUseCase
from app.domain.entities.season import Season
from app.domain.entities.chapter import Chapter
from app.domain.entities.article import Article
from app.domain.entities.zone import Zone
from app.domain.entities.item import Item, ItemUsageReport, ItemType
from app.domain.exceptions.guide import (
    SeasonNotFoundError, SeasonActiveError, SeasonHasProgressError,
    ArticleNotFoundError, ArticleHasUnlocksError,
)
from app.domain.exceptions.zone import ZoneNotFoundError, ZoneHasActiveExpeditionsError
from app.domain.exceptions import ItemNotFoundError, ItemInUseError
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.repositories.item_repository import ItemRepository


# ─── Helpers ──────────────────────────────────────────────────────


def make_active_season(season_id):
    return Season(
        id=season_id,
        name="Active Season",
        description="Currently active",
        start_date=datetime.now(timezone.utc) - timedelta(days=10),
        end_date=datetime.now(timezone.utc) + timedelta(days=10),
        is_active=True,
    )


def make_past_season(season_id):
    return Season(
        id=season_id,
        name="Past Season",
        description="Already ended",
        start_date=datetime.now(timezone.utc) - timedelta(days=20),
        end_date=datetime.now(timezone.utc) - timedelta(days=10),
        is_active=True,
    )


def make_zone(zone_id):
    return Zone(
        id=zone_id,
        name="Test Zone",
        description="A test zone",
        image_url="http://example.com/zone.png",
        fuel_cost=10.0,
        optimism_risk=5.0,
        duration_seconds=60,
    )


def make_item(item_id):
    return Item(
        id=item_id,
        name="Test Item",
        description="A test item",
        type=ItemType.MATERIAL,
    )


def make_article(article_id):
    return Article(
        id=article_id,
        chapter_id=uuid4(),
        title="Test Article",
        content="Test content",
        fragment_cost=5,
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


# ─── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def mock_season_repo():
    repo = MagicMock(spec=SeasonRepository)
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_chapter_repo():
    repo = MagicMock(spec=ChapterRepository)
    repo.get_chapter_by_article_id = AsyncMock()
    repo.get_by_season_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_guide_progress_repo():
    repo = MagicMock(spec=GuideProgressRepository)
    repo.count_unlocked_by_article_id = AsyncMock()
    repo.count_unlocked_by_chapter_ids = AsyncMock()
    return repo


@pytest.fixture
def mock_zone_repo():
    repo = MagicMock(spec=ZoneRepository)
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_expedition_repo():
    repo = MagicMock(spec=ExpeditionRepository)
    repo.count_by_zone_id = AsyncMock()
    return repo


@pytest.fixture
def mock_item_repo():
    repo = MagicMock(spec=ItemRepository)
    repo.get_by_id = AsyncMock()
    repo.check_usage = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.track = MagicMock()
    uow.commit = AsyncMock()
    return uow


# ─── Season tests ─────────────────────────────────────────────────


class TestSoftDeleteSeason:
    @pytest.mark.asyncio
    async def test_delete_nonexistent_season_raises_error(
        self, mock_season_repo, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        mock_season_repo.get_by_id.return_value = None

        use_case = SoftDeleteSeasonUseCase(mock_season_repo, mock_chapter_repo, mock_guide_progress_repo)

        with pytest.raises(SeasonNotFoundError):
            await use_case.execute(uuid4(), mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_active_season_raises_error(
        self, mock_season_repo, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        season_id = uuid4()
        mock_season_repo.get_by_id.return_value = make_active_season(season_id)

        use_case = SoftDeleteSeasonUseCase(mock_season_repo, mock_chapter_repo, mock_guide_progress_repo)

        with pytest.raises(SeasonActiveError, match="Active Season"):
            await use_case.execute(season_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_season_with_unlocked_articles_raises_error(
        self, mock_season_repo, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        season_id = uuid4()
        chapter_id = uuid4()
        chapter = Chapter(
            id=chapter_id, name="Ch", description="D", is_secret=False,
            season_id=season_id, reward_xgen=0, reward_fragments=0,
        )
        mock_season_repo.get_by_id.return_value = make_past_season(season_id)
        mock_chapter_repo.get_by_season_id.return_value = [chapter]
        mock_guide_progress_repo.count_unlocked_by_chapter_ids.return_value = 5

        use_case = SoftDeleteSeasonUseCase(mock_season_repo, mock_chapter_repo, mock_guide_progress_repo)

        with pytest.raises(SeasonHasProgressError, match="Past Season"):
            await use_case.execute(season_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_inactive_season_without_progress_succeeds(
        self, mock_season_repo, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        season_id = uuid4()
        season = make_past_season(season_id)
        mock_season_repo.get_by_id.return_value = season
        mock_chapter_repo.get_by_season_id.return_value = []
        mock_guide_progress_repo.count_unlocked_by_chapter_ids.return_value = 0

        use_case = SoftDeleteSeasonUseCase(mock_season_repo, mock_chapter_repo, mock_guide_progress_repo)

        await use_case.execute(season_id, mock_uow)

        assert season.is_deleted()
        mock_season_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()


# ─── Article tests ────────────────────────────────────────────────


class TestSoftDeleteArticle:
    @pytest.mark.asyncio
    async def test_delete_nonexistent_article_raises_error(
        self, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        mock_chapter_repo.get_chapter_by_article_id.return_value = None

        use_case = SoftDeleteArticleUseCase(mock_chapter_repo, mock_guide_progress_repo)

        with pytest.raises(ArticleNotFoundError):
            await use_case.execute(uuid4(), mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_article_with_unlocks_raises_error(
        self, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        article_id = uuid4()
        chapter_id = uuid4()
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article)

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_guide_progress_repo.count_unlocked_by_article_id.return_value = 3

        use_case = SoftDeleteArticleUseCase(mock_chapter_repo, mock_guide_progress_repo)

        with pytest.raises(ArticleHasUnlocksError, match="3 players"):
            await use_case.execute(article_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_article_without_unlocks_succeeds(
        self, mock_chapter_repo, mock_guide_progress_repo, mock_uow
    ):
        article_id = uuid4()
        chapter_id = uuid4()
        article = make_article(article_id)
        chapter = make_chapter(chapter_id, article)

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_guide_progress_repo.count_unlocked_by_article_id.return_value = 0

        use_case = SoftDeleteArticleUseCase(mock_chapter_repo, mock_guide_progress_repo)

        await use_case.execute(article_id, mock_uow)

        assert article.is_deleted()
        mock_chapter_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()


# ─── Zone tests ───────────────────────────────────────────────────


class TestSoftDeleteZone:
    @pytest.mark.asyncio
    async def test_delete_nonexistent_zone_raises_error(
        self, mock_zone_repo, mock_expedition_repo, mock_uow
    ):
        mock_zone_repo.get_by_id.return_value = None

        use_case = SoftDeleteZoneUseCase(mock_zone_repo, mock_expedition_repo)

        with pytest.raises(ZoneNotFoundError):
            await use_case.execute(uuid4(), mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_zone_with_active_expeditions_raises_error(
        self, mock_zone_repo, mock_expedition_repo, mock_uow
    ):
        zone_id = uuid4()
        mock_zone_repo.get_by_id.return_value = make_zone(zone_id)
        mock_expedition_repo.count_by_zone_id.return_value = 3

        use_case = SoftDeleteZoneUseCase(mock_zone_repo, mock_expedition_repo)

        with pytest.raises(ZoneHasActiveExpeditionsError, match="Test Zone"):
            await use_case.execute(zone_id, mock_uow)

        mock_expedition_repo.count_by_zone_id.assert_awaited_once_with(zone_id)
        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_zone_without_expeditions_succeeds(
        self, mock_zone_repo, mock_expedition_repo, mock_uow
    ):
        zone_id = uuid4()
        zone = make_zone(zone_id)
        mock_zone_repo.get_by_id.return_value = zone
        mock_expedition_repo.count_by_zone_id.return_value = 0

        use_case = SoftDeleteZoneUseCase(mock_zone_repo, mock_expedition_repo)

        await use_case.execute(zone_id, mock_uow)

        assert zone.is_deleted()
        mock_zone_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()


# ─── Item tests ───────────────────────────────────────────────────


class TestSoftDeleteItem:
    @pytest.mark.asyncio
    async def test_delete_nonexistent_item_raises_error(
        self, mock_item_repo, mock_uow
    ):
        mock_item_repo.get_by_id.return_value = None

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        with pytest.raises(ItemNotFoundError):
            await use_case.execute(uuid4(), mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_in_inventory_raises_error(
        self, mock_item_repo, mock_uow
    ):
        item_id = uuid4()
        mock_item_repo.get_by_id.return_value = make_item(item_id)
        mock_item_repo.check_usage.return_value = ItemUsageReport(
            item_id=item_id,
            inventory_count=2,
        )

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        with pytest.raises(ItemInUseError, match="2 player inventories"):
            await use_case.execute(item_id, mock_uow)

        mock_item_repo.save.assert_not_called()
        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_in_zone_loot_table_raises_error(
        self, mock_item_repo, mock_uow
    ):
        item_id = uuid4()
        mock_item_repo.get_by_id.return_value = make_item(item_id)
        mock_item_repo.check_usage.return_value = ItemUsageReport(
            item_id=item_id,
            zone_names=["Alpha Zone", "Beta Zone"],
        )

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        with pytest.raises(ItemInUseError, match="Alpha Zone"):
            await use_case.execute(item_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_in_loot_box_raises_error(
        self, mock_item_repo, mock_uow
    ):
        item_id = uuid4()
        mock_item_repo.get_by_id.return_value = make_item(item_id)
        mock_item_repo.check_usage.return_value = ItemUsageReport(
            item_id=item_id,
            loot_box_names=["Mystery Box"],
        )

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        with pytest.raises(ItemInUseError, match="Mystery Box"):
            await use_case.execute(item_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_in_shop_raises_error(
        self, mock_item_repo, mock_uow
    ):
        item_id = uuid4()
        mock_item_repo.get_by_id.return_value = make_item(item_id)
        mock_item_repo.check_usage.return_value = ItemUsageReport(
            item_id=item_id,
            active_shop_items=1,
        )

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        with pytest.raises(ItemInUseError, match="active shop items"):
            await use_case.execute(item_id, mock_uow)

        mock_uow.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_without_usage_succeeds(
        self, mock_item_repo, mock_uow
    ):
        item_id = uuid4()
        item = make_item(item_id)
        mock_item_repo.get_by_id.return_value = item
        mock_item_repo.check_usage.return_value = ItemUsageReport(
            item_id=item_id,
        )

        use_case = SoftDeleteItemUseCase(mock_item_repo)

        await use_case.execute(item_id, mock_uow)

        assert item.is_deleted()
        mock_item_repo.save.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()
