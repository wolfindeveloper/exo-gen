from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from app.domain.entities.expedition import Expedition


class ExpeditionRepository(ABC):
    @abstractmethod
    async def get_active_by_ship_id(self, ship_id: UUID) -> Expedition | None:
        pass

    @abstractmethod
    async def get_current_by_ship_id(self, ship_id: UUID) -> Expedition | None:
        """Возвращает последнюю экспедицию корабля, которая ещё не завершена (IN_PROGRESS или FINISHED)"""
        pass

    @abstractmethod
    async def get_by_id(self, expedition_id: UUID, for_update: bool = False) -> Expedition | None:
        pass

    @abstractmethod
    async def get_finished_expeditions(self) -> list[Expedition]:
        pass

    @abstractmethod
    async def count_by_zone_id(self, zone_id: UUID) -> int:
        """Возвращает количество активных экспедиций (IN_PROGRESS, FINISHED) в указанной зоне"""
        pass

    @abstractmethod
    async def count_running_by_zone_id(self, zone_id: UUID, now: datetime) -> int:
        """Возвращает количество экспедиций IN_PROGRESS с ends_at > now в указанной зоне"""
        pass

    @abstractmethod
    async def save(self, expedition: Expedition) -> None:
        pass