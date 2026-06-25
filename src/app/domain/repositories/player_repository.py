from abc import ABC, abstractmethod
from app.domain.entities.player import Player


class PlayerRepository(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Player | None:
        pass
        

    @abstractmethod
    async def save(self, player: Player) -> None:
        pass