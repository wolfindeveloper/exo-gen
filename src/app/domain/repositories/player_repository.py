from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.player import Player


class PlayerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, player_id: UUID) -> Player | None:
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Player | None:
        pass

    @abstractmethod
    async def get_by_ship_id(self, ship_id: UUID) -> Player | None:
        pass

    @abstractmethod
    async def get_by_id_for_update(self, player_id: UUID) -> Player | None:
        """Загружает игрока с блокировкой строки (SELECT ... FOR UPDATE)"""
        pass

    @abstractmethod
    async def save(self, player: Player) -> None:
        pass

    @abstractmethod
    async def get_top_players_by_xp(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        """Возвращает топ игроков по XP: список (username, xp, id)"""
        pass

    @abstractmethod
    async def get_player_rank_by_xp(self, player_id: UUID) -> int:
        """Возвращает место игрока в глобальном рейтинге по XP (1-based)"""
        pass

    @abstractmethod
    async def get_top_players_by_total_expeditions(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        """Топ игроков по количеству экспедиций: список (username, total_expeditions, id)"""
        pass

    @abstractmethod
    async def get_top_players_by_total_artifacts_found(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        """Топ игроков по количеству найденных артефактов: список (username, total_artifacts_found, id)"""
        pass

    @abstractmethod
    async def get_top_players_by_xgen_balance(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        """Топ игроков по балансу XGen: список (username, xgen_balance, id)"""
        pass

    @abstractmethod
    async def get_player_rank_by_total_expeditions(self, player_id: UUID) -> int:
        """Место игрока в рейтинге по количеству экспедиций (1-based)"""
        pass

    @abstractmethod
    async def get_player_rank_by_total_artifacts_found(self, player_id: UUID) -> int:
        """Место игрока в рейтинге по найденным артефактам (1-based)"""
        pass

    @abstractmethod
    async def get_player_rank_by_xgen_balance(self, player_id: UUID) -> int:
        """Место игрока в рейтинге по балансу XGen (1-based)"""
        pass