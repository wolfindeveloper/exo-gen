from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.equipment import Equipment


class EquipmentRepository(ABC):
    @abstractmethod
    async def get_by_ship_id(self, ship_id: UUID) -> Equipment | None:
        pass

    @abstractmethod
    async def save(self, equipment: Equipment) -> None:
        pass
