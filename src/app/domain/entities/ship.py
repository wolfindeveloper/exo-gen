import uuid
from dataclasses import dataclass
from uuid import UUID
from datetime import timedelta

from app.domain.entities.zone import Zone
from app.domain.entities.expedition import Expedition, ExpeditionStatus
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
    speed: float = 1.0 # Скорость
    defense: float = 0.0 # Защита
    luck: float = 0.0 # Шанс

    def can_start_expedition(self, zone: Zone) -> bool:
        return self.tea_level.value >= zone.fuel_cost and not self.optimism.is_destroyed()
            
        

    def start_expedition(self, zone: Zone, clock: Clock = None) -> Expedition:
        if clock is None:
            clock = SystemClock()

        if self.optimism.is_destroyed():
            raise ShipDestroyedError("Ship optimism is 0, cannot start expedition")

        if self.tea_level.value < zone.fuel_cost:
            raise InsufficientTeaError(required=zone.fuel_cost, available=self.tea_level.value)

        self.tea_level = self.tea_level.consume(zone.fuel_cost)
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
        self.optimism = self.optimism.apply_damage(risk, self.defense)

    def restore_tea(self, amount: float) -> None:
        self.tea_level = self.tea_level.restore(amount)

    def restore_optimism(self, amount: float) -> None:
        self.optimism = self.optimism.restore(amount)
        