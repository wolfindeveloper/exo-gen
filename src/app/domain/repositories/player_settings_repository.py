from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.player_settings import PlayerSettings


class PlayerSettingsRepository(ABC):
    @abstractmethod
    async def get_by_player_id(self, player_id: UUID) -> PlayerSettings | None:
        pass

    @abstractmethod
    async def save(self, settings: PlayerSettings) -> None:
        pass
