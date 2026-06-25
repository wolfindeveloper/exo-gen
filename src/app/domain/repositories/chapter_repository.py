from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.chapter import Chapter


class ChapterRepository(ABC):
    @abstractmethod
    async def get_all_with_articles(self) -> list[Chapter]:
        """Возвращает все главы вместе со статьями (для проверки доступности)"""
        pass

    @abstractmethod
    async def get_by_id(self, chapter_id: UUID) -> Chapter | None:
        pass

    @abstractmethod
    async def get_chapter_by_article_id(self, article_id: UUID) -> Chapter | None:
        pass