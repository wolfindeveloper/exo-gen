from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.zone import Zone


class ZoneRepository(ABC):
    @abstractmethod
    async def get_all(self) -> list[Zone]:
        pass

    @abstractmethod
    async def get_by_id(self, zone_id: UUID) -> Zone | None:
        pass
        

    @abstractmethod
    async def save(self, zone: Zone) -> None:
        pass