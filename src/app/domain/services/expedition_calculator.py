from dataclasses import dataclass

from app.domain.entities.zone import Zone
from app.domain.entities.ship import Ship
from app.domain.entities.equipment import Equipment


@dataclass(frozen=True)
class ExpeditionPreview:
    effective_fuel_cost: float
    effective_duration_seconds: float
    estimated_damage_percent: float
    risk_percent: float
    fuel_ok: bool
    artifact_bonuses: dict[str, float]


class ExpeditionCalculatorService:
    """Pure domain service for expedition stat preview calculations.
    Mirrors frontend/src/lib/expeditionCalc.ts formulas 1:1.
    """

    @staticmethod
    def compute_preview(
        zone: Zone,
        ship: Ship,
        equipment: Equipment | None = None,
    ) -> ExpeditionPreview:
        base_stats = {
            "speed": ship.speed,
            "defense": ship.defense,
            "fuel_efficiency": 0.0,
        }
        if equipment:
            bonuses = equipment.get_total_bonuses()
            for key, value in bonuses.items():
                base_stats[key] = base_stats.get(key, 0) + value

        speed_mod = max(base_stats.get("speed", ship.speed), 0.1)
        total_defense = base_stats.get("defense", ship.defense)
        fuel_efficiency = base_stats.get("fuel_efficiency", 0.0)

        artifact_bonuses: dict[str, float] = {}
        if speed_mod != 1.0:
            artifact_bonuses["speed_mod"] = speed_mod - 1.0
        if total_defense > 0:
            artifact_bonuses["damage_reduction"] = total_defense
        if fuel_efficiency > 0:
            artifact_bonuses["fuel_efficiency"] = fuel_efficiency

        total_damage_reduction = artifact_bonuses.get("damage_reduction", 0.0)
        total_fuel_efficiency = artifact_bonuses.get("fuel_efficiency", 0.0)

        effective_risk = max(0.0, zone.optimism_risk - total_damage_reduction)
        effective_fuel_cost = zone.fuel_cost * (1.0 - total_fuel_efficiency)
        zone_duration_hours = zone.duration_seconds / 3600.0
        effective_duration = zone_duration_hours / speed_mod

        effective_fuel_cost = max(0.0, round(effective_fuel_cost))
        fuel_ok = ship.tea_level.value >= effective_fuel_cost

        optimism_value = ship.optimism.value
        if optimism_value > 0:
            estimated_damage = round((effective_risk / (optimism_value / 100.0)) * 100.0 * 10.0) / 10.0
        else:
            estimated_damage = 0.0

        risk_percent = min(100.0, round(effective_risk * 100.0))
        duration_seconds = effective_duration * 3600.0

        return ExpeditionPreview(
            effective_fuel_cost=effective_fuel_cost,
            effective_duration_seconds=duration_seconds,
            estimated_damage_percent=estimated_damage,
            risk_percent=risk_percent,
            fuel_ok=fuel_ok,
            artifact_bonuses=artifact_bonuses,
        )
