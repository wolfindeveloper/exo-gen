from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion, ArticleTriggerProgress
from app.domain.entities.leaderboard_entry import LeaderboardEntry


class GuideProgressRepository(ABC):
    @abstractmethod
    async def get_unlocked_articles_ids(self, player_id: UUID) -> set[UUID]:
        """Возвращает множество ID статей, которые игрок уже открыл"""
        pass

    @abstractmethod
    async def save_unlocked_article(self, unlocked: UnlockedArticle) -> None:
        pass

    @abstractmethod
    async def save_chapter_completion(self, completion: ChapterCompletion) -> None:
        pass

    @abstractmethod
    async def is_chapter_completed(self, player_id: UUID, chapter_id: UUID) -> bool:
        pass

    @abstractmethod
    async def is_article_unlocked(self, player_id: UUID, article_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_trigger_progress(self, player_id: UUID, article_id: UUID) -> ArticleTriggerProgress | None:
        pass

    @abstractmethod
    async def save_trigger_progress(self, progress: ArticleTriggerProgress) -> None:
        pass

    @abstractmethod
    async def get_season_leaderboard(self, season_id: UUID, limit: int = 100) -> list[LeaderboardEntry]:
        """Возвращает топ игроков, завершивших главы указанного сезона"""
        pass

    @abstractmethod
    async def get_top_players_by_unlocked_articles(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        """Топ игроков по количеству открытых статей: список (username, count, id)"""
        pass

    @abstractmethod
    async def get_player_rank_by_unlocked_articles(self, player_id: UUID) -> int:
        """Место игрока в рейтинге по открытым статьям (1-based)"""
        pass