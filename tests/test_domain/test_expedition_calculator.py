import uuid

from app.domain.entities.zone import Zone
from app.domain.entities.ship import Ship
from app.domain.entities.equipment import Equipment, EquippedArtifact
from app.domain.services.expedition_calculator import ExpeditionCalculatorService
from app.domain.value_objects.resources import TeaLevel, Optimism


def _make_zone(
    fuel_cost: float = 10.0,
    optimism_risk: float = 0.1,
    duration_seconds: int = 14400,
) -> Zone:
    return Zone(
        id=uuid.uuid4(),
        name="Test Zone",
        description="...",
        image_url="",
        fuel_cost=fuel_cost,
        optimism_risk=optimism_risk,
        duration_seconds=duration_seconds,
    )


def _make_ship(
    tea_level: float = 100.0,
    optimism: float = 100.0,
    speed: float = 1.0,
    defense: float = 0.0,
) -> Ship:
    return Ship(
        id=uuid.uuid4(),
        player_id=uuid.uuid4(),
        tea_level=TeaLevel(tea_level),
        optimism=Optimism(optimism),
        speed=speed,
        defense=defense,
    )


class TestExpeditionCalculatorBaseline:
    def test_no_artifacts_risk_01_optimism_100(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.2)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.risk_percent == 10
        assert result.estimated_damage_percent == 10
        assert result.fuel_ok is True

    def test_high_risk_zone(self):
        zone = _make_zone(fuel_cost=20, optimism_risk=0.5, duration_seconds=28800)
        ship = _make_ship(tea_level=200, optimism=100, speed=1.0)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.risk_percent == 50
        assert result.estimated_damage_percent == 50

    def test_defense_reduces_damage(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.5, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.0, defense=0.2)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.risk_percent == 30
        assert result.estimated_damage_percent == 30

    def test_defense_negates_risk(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.0, defense=0.15)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.risk_percent == 0
        assert result.estimated_damage_percent == 0

    def test_damage_scales_with_current_optimism(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=50, speed=1.0)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.estimated_damage_percent == 5

    def test_speed_reduces_duration(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship_fast = _make_ship(tea_level=100, optimism=100, speed=2.0)
        ship_slow = _make_ship(tea_level=100, optimism=100, speed=1.0)

        result_fast = ExpeditionCalculatorService.compute_preview(zone, ship_fast)
        result_slow = ExpeditionCalculatorService.compute_preview(zone, ship_slow)

        assert result_fast.effective_duration_seconds < result_slow.effective_duration_seconds

    def test_fuel_efficiency_reduces_cost(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.0)

        equipment = Equipment(
            ship_id=ship.id,
            artifacts=[EquippedArtifact(item_id=uuid.uuid4(), bonuses={"fuel_efficiency": 0.2})],
        )

        result = ExpeditionCalculatorService.compute_preview(zone, ship, equipment)

        assert result.effective_fuel_cost == 8

    def test_insufficient_fuel(self):
        zone = _make_zone(fuel_cost=15, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=10, optimism=100, speed=1.0)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert result.fuel_ok is False

    def test_artifact_bonuses_populated(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.3, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.0, defense=0.1)

        result = ExpeditionCalculatorService.compute_preview(zone, ship)

        assert "damage_reduction" in result.artifact_bonuses
        assert result.artifact_bonuses["damage_reduction"] == 0.1

    def test_speed_artifact_bonuses(self):
        zone = _make_zone(fuel_cost=10, optimism_risk=0.1, duration_seconds=14400)
        ship = _make_ship(tea_level=100, optimism=100, speed=1.0)

        equipment = Equipment(
            ship_id=ship.id,
            artifacts=[EquippedArtifact(item_id=uuid.uuid4(), bonuses={"speed": 0.2})],
        )

        result = ExpeditionCalculatorService.compute_preview(zone, ship, equipment)

        assert "speed_mod" in result.artifact_bonuses
        assert abs(result.artifact_bonuses["speed_mod"] - 0.2) < 1e-9
