from pydantic import BaseModel


class ZonePreviewDTO(BaseModel):
    effective_fuel_cost: float
    effective_duration_seconds: float
    estimated_damage_percent: float
    risk_percent: float
    fuel_ok: bool
    artifact_bonuses: dict[str, float]
