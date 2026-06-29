from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.season import Season


class SeasonRepository(ABC):
    @abstractmethod
    async def get_by_id(self, season_id: UUID) -> Season | None:
        pass

    @abstractmethod
    async def get_active_seasons(self) -> list[Season]:
        """Возвращает все активные сезоны (start_date <= now <= end_date)"""
        pass
