from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

import pytest

from app.domain.entities.player import Player
from app.domain.entities.chapter import Chapter
from app.domain.entities.article import Article
from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.value_objects.resources import XgenBalance, FragmentsBalance
from app.application.use_cases.get_guide import GetGuideUseCase
from app.application.use_cases.unlock_article import UnlockArticleUseCase
from app.application.use_cases.process_trigger import ProcessTriggerUseCase
from app.application.dtos.guide_dto import TriggerEventDTO


@pytest.fixture
def mock_chapter_repo():
    repo = MagicMock(spec=ChapterRepository)
    repo.get_all_with_articles = AsyncMock()
    repo.get_chapter_by_article_id = AsyncMock()
    repo.get_paginated_articles = AsyncMock()
    return repo


@pytest.fixture
def mock_season_repo():
    repo = MagicMock(spec=SeasonRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_progress_repo():
    repo = MagicMock(spec=GuideProgressRepository)
    repo.get_unlocked_articles_ids = AsyncMock()
    repo.is_chapter_completed = AsyncMock()
    repo.is_article_unlocked = AsyncMock()
    repo.save_unlocked_article = AsyncMock()
    repo.save_chapter_completion = AsyncMock()
    repo.get_trigger_progress = AsyncMock()
    repo.save_trigger_progress = AsyncMock()
    return repo


@pytest.fixture
def mock_inventory_repo():
    repo = MagicMock()
    repo.get_by_player_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_loot_box_service():
    return MagicMock()


@pytest.fixture
def mock_loot_box_repo():
    repo = MagicMock()
    repo.get_by_type = AsyncMock()
    return repo


@pytest.fixture
def mock_item_repo():
    repo = MagicMock()
    repo.get_by_ids = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def sample_player():
    return Player(
        id=uuid4(),
        telegram_id=123456,
        username="test_user",
        xp=100,
        xgen_balance=XgenBalance(500),
        fragments_balance=FragmentsBalance(100),
    )


@pytest.fixture
def sample_article():
    return Article(
        id=uuid4(),
        chapter_id=uuid4(),
        title="Test Article",
        content="Test content",
        fragment_cost=10,
        trigger_event_type=None,
        trigger_threshold=1,
    )


@pytest.fixture
def sample_chapter(sample_article):
    return Chapter(
        id=sample_article.chapter_id,
        name="Test Chapter",
        description="Test description",
        is_secret=False,
        reward_xgen=50,
        reward_fragments=20,
        articles=[sample_article],
    )


class TestGetGuideUseCase:
    """Tests for GetGuideUseCase - seasonal chapters filtering."""

    @pytest.mark.asyncio
    async def test_seasonal_chapter_hidden_when_expired(
        self, mock_chapter_repo, mock_season_repo, mock_progress_repo, sample_player
    ):
        """Expired seasonal chapter should be hidden if not completed."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Seasonal Article",
            content="Secret content",
            fragment_cost=10,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Seasonal Chapter",
            description="Seasonal",
            is_secret=False,
            season_id=uuid4(),
            articles=[article],
        )

        season = MagicMock()
        season.is_currently_active.return_value = False
        mock_season_repo.get_by_id.return_value = season
        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.get_unlocked_articles_ids.return_value = set()
        mock_progress_repo.is_chapter_completed.return_value = False

        use_case = GetGuideUseCase(mock_chapter_repo, mock_season_repo, mock_progress_repo)
        result = await use_case.execute(sample_player)

        assert len(result.chapters) == 0

    @pytest.mark.asyncio
    async def test_seasonal_chapter_shown_when_active(
        self, mock_chapter_repo, mock_season_repo, mock_progress_repo, sample_player
    ):
        """Active seasonal chapter should be visible."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Active Article",
            content="Active content",
            fragment_cost=10,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Active Chapter",
            description="Active",
            is_secret=False,
            season_id=uuid4(),
            articles=[article],
        )

        season = MagicMock()
        season.is_currently_active.return_value = True
        mock_season_repo.get_by_id.return_value = season
        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.get_unlocked_articles_ids.return_value = set()
        mock_progress_repo.is_chapter_completed.return_value = False

        use_case = GetGuideUseCase(mock_chapter_repo, mock_season_repo, mock_progress_repo)
        result = await use_case.execute(sample_player)

        assert len(result.chapters) == 1
        assert result.chapters[0].name == "Active Chapter"

    @pytest.mark.asyncio
    async def test_expired_seasonal_chapter_shown_if_completed(
        self, mock_chapter_repo, mock_season_repo, mock_progress_repo, sample_player
    ):
        """Expired seasonal chapter should be visible if player completed it."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Completed Article",
            content="Completed content",
            fragment_cost=10,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Completed Chapter",
            description="Completed",
            is_secret=False,
            season_id=uuid4(),
            articles=[article],
        )

        season = MagicMock()
        season.is_currently_active.return_value = False
        mock_season_repo.get_by_id.return_value = season
        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.get_unlocked_articles_ids.return_value = {article.id}
        mock_progress_repo.is_chapter_completed.return_value = True

        use_case = GetGuideUseCase(mock_chapter_repo, mock_season_repo, mock_progress_repo)
        result = await use_case.execute(sample_player)

        assert len(result.chapters) == 1
        assert result.chapters[0].reward_claimed is True

    @pytest.mark.asyncio
    async def test_article_content_hidden_when_not_unlocked(
        self, mock_chapter_repo, mock_season_repo, mock_progress_repo, sample_player
    ):
        """Article content should be None when not unlocked."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Locked Article",
            content="Hidden content",
            fragment_cost=10,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Test Chapter",
            description="Test",
            is_secret=False,
            articles=[article],
        )

        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.get_unlocked_articles_ids.return_value = set()
        mock_progress_repo.is_chapter_completed.return_value = False

        use_case = GetGuideUseCase(mock_chapter_repo, mock_season_repo, mock_progress_repo)
        result = await use_case.execute(sample_player)

        assert result.chapters[0].articles[0].content is None
        assert result.chapters[0].articles[0].is_unlocked is False


class TestUnlockArticleUseCase:
    """Tests for UnlockArticleUseCase - fragments deduction."""

    @pytest.mark.asyncio
    async def test_fragments_deducted_on_unlock(
        self, mock_chapter_repo, mock_progress_repo, mock_inventory_repo,
        mock_loot_box_service, mock_loot_box_repo, mock_item_repo, sample_player
    ):
        """Fragments should be deducted when unlocking article."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Paid Article",
            content="Paid content",
            fragment_cost=25,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Test Chapter",
            description="Test",
            is_secret=False,
            articles=[article],
        )

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_progress_repo.is_article_unlocked.return_value = False
        mock_inventory_repo.get_by_player_id.return_value = MagicMock()
        mock_progress_repo.get_unlocked_articles_ids.return_value = {article.id}

        mock_player_repo = MagicMock()
        mock_player_repo.save = AsyncMock()

        use_case = UnlockArticleUseCase(
            player_repo=mock_player_repo,
            chapter_repo=mock_chapter_repo,
            season_repo=MagicMock(),
            guide_repo=mock_progress_repo,
            loot_box_service=mock_loot_box_service,
            loot_box_repo=mock_loot_box_repo,
            inventory_repo=mock_inventory_repo,
            item_repo=mock_item_repo,
        )

        uow = MagicMock()
        uow.track = MagicMock()
        uow.commit = AsyncMock()

        await use_case.execute(sample_player, article.id, uow)

        assert sample_player.fragments_balance.value == 75

    @pytest.mark.asyncio
    async def test_insufficient_fragments_raises_error(
        self, mock_chapter_repo, mock_progress_repo, mock_inventory_repo,
        mock_loot_box_service, mock_loot_box_repo, mock_item_repo, sample_player
    ):
        """Should raise error when player has insufficient fragments."""
        sample_player.fragments_balance = FragmentsBalance(5)

        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Expensive Article",
            content="Expensive content",
            fragment_cost=25,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Test Chapter",
            description="Test",
            is_secret=False,
            articles=[article],
        )

        mock_chapter_repo.get_chapter_by_article_id.return_value = chapter
        mock_progress_repo.is_article_unlocked.return_value = False
        mock_inventory_repo.get_by_player_id.return_value = MagicMock()

        use_case = UnlockArticleUseCase(
            player_repo=MagicMock(),
            chapter_repo=mock_chapter_repo,
            season_repo=MagicMock(),
            guide_repo=mock_progress_repo,
            loot_box_service=mock_loot_box_service,
            loot_box_repo=mock_loot_box_repo,
            inventory_repo=mock_inventory_repo,
            item_repo=mock_item_repo,
        )

        uow = MagicMock()
        uow.track = MagicMock()
        uow.commit = AsyncMock()

        with pytest.raises(Exception):
            await use_case.execute(sample_player, article.id, uow)

        assert sample_player.fragments_balance.value == 5


class TestProcessTriggerUseCase:
    """Tests for ProcessTriggerUseCase - all trigger types."""

    @pytest.mark.asyncio
    async def test_expedition_count_trigger(
        self, mock_chapter_repo, mock_progress_repo, sample_player
    ):
        """Trigger should work with expedition_completed event type."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Expedition Article",
            content="Expedition content",
            fragment_cost=0,
            trigger_event_type="expedition_completed",
            trigger_threshold=3,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Expedition Chapter",
            description="Expedition",
            is_secret=False,
            articles=[article],
        )

        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.is_article_unlocked.return_value = False
        mock_progress_repo.get_trigger_progress.return_value = None
        mock_progress_repo.get_unlocked_articles_ids.return_value = {article.id}

        use_case = ProcessTriggerUseCase(
            player_repo=MagicMock(),
            chapter_repo=mock_chapter_repo,
            season_repo=MagicMock(),
            guide_repo=mock_progress_repo,
            loot_box_service=MagicMock(),
            loot_box_repo=MagicMock(),
            inventory_repo=MagicMock(),
            item_repo=MagicMock(),
        )

        uow = MagicMock()
        uow.track = MagicMock()
        uow.commit = AsyncMock()

        dto = TriggerEventDTO(event_type="expedition_completed", count=1)
        result = await use_case.execute(sample_player, dto, uow)

        assert len(result.newly_unlocked_articles) == 0

    @pytest.mark.asyncio
    async def test_trigger_unlocks_after_threshold(
        self, mock_chapter_repo, mock_progress_repo, sample_player
    ):
        """Article should unlock when threshold is reached."""
        article = Article(
            id=uuid4(),
            chapter_id=uuid4(),
            title="Threshold Article",
            content="Threshold content",
            fragment_cost=0,
            trigger_event_type="daily_login",
            trigger_threshold=5,
        )
        chapter = Chapter(
            id=article.chapter_id,
            name="Login Chapter",
            description="Login",
            is_secret=False,
            articles=[article],
        )

        mock_chapter_repo.get_all_with_articles.return_value = [chapter]
        mock_progress_repo.is_article_unlocked.return_value = False

        progress = MagicMock()
        progress.increment.return_value = True
        mock_progress_repo.get_trigger_progress.return_value = progress
        mock_progress_repo.get_unlocked_articles_ids.return_value = {article.id}

        use_case = ProcessTriggerUseCase(
            player_repo=MagicMock(),
            chapter_repo=mock_chapter_repo,
            season_repo=MagicMock(),
            guide_repo=mock_progress_repo,
            loot_box_service=MagicMock(),
            loot_box_repo=MagicMock(),
            inventory_repo=MagicMock(),
            item_repo=MagicMock(),
        )

        uow = MagicMock()
        uow.track = MagicMock()
        uow.commit = AsyncMock()

        dto = TriggerEventDTO(event_type="daily_login", count=1)
        result = await use_case.execute(sample_player, dto, uow)

        assert len(result.newly_unlocked_articles) == 1
        assert result.newly_unlocked_articles[0] == "Threshold Article"
