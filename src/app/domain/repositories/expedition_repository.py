from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.expedition import Expedition


class ExpeditionRepository(ABC):
    @abstractmethod
    async def get_active_by_ship_id(self, ship_id: UUID) -> Expedition | None:
        pass


    @abstractmethod
    async def get_by_id(self, expedition_id: UUID, for_update: bool = False) -> Expedition | None:
        pass


    @abstractmethod
    async def get_finished_expeditions(self) -> list[Expedition]:
        pass


    @abstractmethod
    async def save(self, expedition: Expedition) -> None:
        pass