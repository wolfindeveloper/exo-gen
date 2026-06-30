from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.article import Article
from app.domain.entities.chapter import Chapter


class ChapterRepository(ABC):
    @abstractmethod
    async def save(self, chapter: Chapter) -> None:
        """Сохраняет новую главу или обновляет существующую (каскадно со статьями)"""
        pass

    @abstractmethod
    async def get_all_with_articles(self) -> list[Chapter]:
        """Возвращает все главы вместе со статьями (для проверки доступности)"""
        pass

    @abstractmethod
    async def get_by_id(self, chapter_id: UUID) -> Chapter | None:
        pass

    @abstractmethod
    async def get_by_season_id(self, season_id: UUID) -> list[Chapter]:
        pass

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Chapter], int]:
        pass

    @abstractmethod
    async def get_paginated_articles(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Article], int]:
        pass

    @abstractmethod
    async def get_chapter_by_article_id(self, article_id: UUID) -> Chapter | None:
        pass