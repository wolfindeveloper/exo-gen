"""Сервис прогрессии игрока: уровни, разблокировки зон и слотов артефактов.

Чистый domain service — никаких импортов из infrastructure/presentation.
Все пороги — единый источник истины для use cases и frontend.
"""
from dataclasses import dataclass


# ── Таблица разблокировок зон по уровням ────────────────────────
# tier: уровень зоны (1-5)
# required_level: минимальный уровень игрока для доступа
ZONE_UNLOCK_TABLE: dict[int, int] = {
    1: 1,   # T1 доступна сразу
    2: 3,   # T2 на 3 уровне
    3: 8,   # T3 на 8 уровне
    4: 12,  # T4 на 12 уровне
    5: 25,  # T5 на 25 уровне
}

# ── Таблица разблокировок слотов артефактов по уровням ──────────
# level_threshold: уровень при достижении которого открываются новые слоты
# slots: общее количество доступных слотов после этого уровня
SLOT_UNLOCK_TABLE: list[tuple[int, int]] = [
    (1,  4),   # Старт: 4 слота
    (5,  6),   # Уровень 5: 6 слотов
    (15, 8),   # Уровень 15: все 8 слотов
]

# ── XP формула ──────────────────────────────────────────────────
XP_PER_HOUR = 20
XP_RISK_MULTIPLIER = 2
XP_MIN_PER_EXPEDITION = 5
XP_PER_LEVEL = 1000  # level = xp // XP_PER_LEVEL


@dataclass(frozen=True)
class UnlockStatus:
    """Статус разблокировки для UI."""
    is_unlocked: bool
    required_level: int | None = None  # None если уже открыто
    current_level: int = 0


class LevelProgressionService:
    """Единый сервис для всех расчётов прогрессии игрока."""

    @staticmethod
    def calculate_level(xp: int) -> int:
        """Вычисляет текущий уровень игрока по его XP."""
        if xp < 0:
            return 1
        return max(1, xp // XP_PER_LEVEL)

    @staticmethod
    def calculate_expedition_xp(duration_seconds: int, optimism_risk: float) -> int:
        """Рассчитывает XP за экспедицию.

        Args:
            duration_seconds: длительность экспедиции в секундах
            optimism_risk: риск зоны как доля (0.05 = 5%)

        Returns:
            Начисляемый XP (всегда >= XP_MIN_PER_EXPEDITION)
        """
        duration_hours = duration_seconds / 3600
        risk_percent = optimism_risk * 100
        raw_xp = int(XP_PER_HOUR * duration_hours + XP_RISK_MULTIPLIER * risk_percent)
        return max(XP_MIN_PER_EXPEDITION, raw_xp)

    @staticmethod
    def get_max_artifact_slots(player_level: int) -> int:
        """Возвращает максимальное количество слотов артефактов для данного уровня."""
        max_slots = SLOT_UNLOCK_TABLE[0][1]  # значение для уровня 1
        for level_threshold, slots in SLOT_UNLOCK_TABLE:
            if player_level >= level_threshold:
                max_slots = slots
            else:
                break
        return max_slots

    @staticmethod
    def get_next_slot_unlock(player_level: int) -> tuple[int, int] | None:
        """Возвращает (required_level, new_slot_count) для следующего открытия слотов.

        Returns None если все слоты уже открыты.
        """
        for level_threshold, slots in SLOT_UNLOCK_TABLE:
            if player_level < level_threshold:
                return (level_threshold, slots)
        return None

    @staticmethod
    def can_access_zone(player_level: int, zone_tier: int) -> UnlockStatus:
        """Проверяет, может ли игрок войти в зону данного тира."""
        required = ZONE_UNLOCK_TABLE.get(zone_tier, 1)
        if player_level >= required:
            return UnlockStatus(is_unlocked=True, current_level=player_level)
        return UnlockStatus(
            is_unlocked=False,
            required_level=required,
            current_level=player_level,
        )

    @staticmethod
    def get_zone_tiers_unlocked(player_level: int) -> list[int]:
        """Возвращает список всех доступных тиров зон для данного уровня."""
        return [tier for tier, req in ZONE_UNLOCK_TABLE.items() if player_level >= req]

    @staticmethod
    def get_next_zone_unlock(player_level: int) -> tuple[int, int] | None:
        """Возвращает (required_level, tier) для следующего открытия тира зоны.

        Returns None если все тиры уже открыты.
        """
        for tier in sorted(ZONE_UNLOCK_TABLE.keys()):
            required = ZONE_UNLOCK_TABLE[tier]
            if player_level < required:
                return (required, tier)
        return None
