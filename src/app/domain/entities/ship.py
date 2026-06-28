import uuid
from dataclasses import dataclass
from uuid import UUID
from datetime import timedelta

from app.domain.entities.zone import Zone
from app.domain.entities.expedition import Expedition, ExpeditionStatus
from app.domain.entities.equipment import Equipment
from app.domain.exceptions.ship import InsufficientTeaError, ShipDestroyedError
from app.domain.services.clock import Clock, SystemClock
from app.domain.value_objects.resources import TeaLevel, Optimism


@dataclass
class Ship:
    id: UUID
    player_id: UUID
    name: str = "Vogon MK"
    tea_level: TeaLevel = TeaLevel(100.0)
    optimism: Optimism = Optimism(100.0)
    speed: float = 1.0
    defense: float = 0.0
    luck: float = 0.0
    equipment: Equipment | None = None

    def get_effective_stats(self) -> dict:
        stats: dict[str, float] = {
            "speed": self.speed,
            "defense": self.defense,
            "luck": self.luck,
            "capacity": 100.0,
            "fuel_efficiency": 0.0,
        }
        if self.equipment:
            bonuses = self.equipment.get_total_bonuses()
            for key, value in bonuses.items():
                stats[key] = stats.get(key, 0) + value
        return stats

    def can_start_expedition(self, zone: Zone) -> bool:
        effective_stats = self.get_effective_stats()
        fuel_efficiency = effective_stats.get("fuel_efficiency", 0.0)
        effective_fuel_cost = max(0.0, zone.fuel_cost * (1.0 - fuel_efficiency))
        return self.tea_level.value >= effective_fuel_cost and not self.optimism.is_destroyed()

    def start_expedition(self, zone: Zone, clock: Clock = None) -> Expedition:
        if clock is None:
            clock = SystemClock()

        if self.optimism.is_destroyed():
            raise ShipDestroyedError("Ship optimism is 0, cannot start expedition")

        effective_stats = self.get_effective_stats()
        fuel_efficiency = effective_stats.get("fuel_efficiency", 0.0)
        effective_fuel_cost = max(0.0, zone.fuel_cost * (1.0 - fuel_efficiency))

        if self.tea_level.value < effective_fuel_cost:
            raise InsufficientTeaError(required=effective_fuel_cost, available=self.tea_level.value)

        self.tea_level = self.tea_level.consume(effective_fuel_cost)
        now = clock.now()
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
        effective_stats = self.get_effective_stats()
        self.optimism = self.optimism.apply_damage(risk, effective_stats.get("defense", self.defense))

    def restore_tea(self, amount: float) -> None:
        effective_stats = self.get_effective_stats()
        self.tea_level = self.tea_level.restore(amount, effective_stats.get("capacity", 100.0))

    def restore_optimism(self, amount: float) -> None:
        self.optimism = self.optimism.restore(amount)
        