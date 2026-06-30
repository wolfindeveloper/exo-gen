from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.season import Season


class SeasonRepository(ABC):
    @abstractmethod
    async def save(self, season: Season) -> None:
        """Сохраняет новый сезон или обновляет существующий"""
        pass

    @abstractmethod
    async def get_by_id(self, season_id: UUID) -> Season | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Season]:
        """Возвращает все сезоны"""
        pass

    @abstractmethod
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Season], int]:
        pass

    @abstractmethod
    async def get_active_seasons(self) -> list[Season]:
        """Возвращает все активные сезоны (start_date <= now <= end_date)"""
        pass
