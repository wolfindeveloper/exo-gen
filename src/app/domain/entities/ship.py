import uuid
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.domain.entities.zone import Zone
from app.domain.entities.expedition import Expedition, ExpeditionStatus


@dataclass
class Ship:
    id: UUID
    player_id: UUID
    name: str = "Vogon MK"
    tea_level: float = 100.0 # Топливо
    optimism: float = 100.0 # Прочность
    speed: float = 1.0 # Скорость
    defense: float = 0.0 # Защита
    luck: float = 0.0 # Шанс

    def can_start_expedition(self, zone: Zone) -> bool:
        return self.tea_level >= zone.fuel_cost and self.optimism > 0
            
        

    def start_expedition(self, zone: Zone) -> Expedition:
        if not self.can_start_expedition(zone):
            raise ValueError("Недостаточно ресурсов или корабль уничтожен")

        self.tea_level -= zone.fuel_cost
        now = datetime.now(timezone.utc)
        ends_at = now + timedelta(seconds=zone.duration_seconds)

        return Expedition(
            id=uuid.uuid4(),
            ship_id=self.id,
            zone_id=zone.id,
            started_at=now,
            ends_at=ends_at,
            status=ExpeditionStatus.IN_PROGRESS
        )

    def apply_expedition_wear_and_tear(self, risk: float):
        """
        Рассчитывает потерю оптимизма (прочности) после экспедиции.
        Защита корабля снижает получаемый урон.
        """
        # Урон не может быть отрицательным

        damage = max(0.0, risk - self.defense)
        self.optimism -= damage

        # Оптимизм не может уйти в минус (корабль не может быть "сломаннее" чем на 0)
        if self.optimism < 0.0:
            self.optimism = 0.0

    def restore_tea(self, amount: float) -> None:
        """Восстанавливает топливо (чай)."""
        self.tea_level += amount
        # В будущем здесь можно добавить проверку на максимальную вместимость бака

    def restore_optimism(self, amount: float) -> None:
        """Восстанавливает прочность (оптимизм)."""
        self.optimism += amount
        # В будущем можно добавить проверку на максимальный уровень оптимизма
        