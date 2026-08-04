from uuid import UUID

from app.domain.entities.player import Player
from app.domain.exceptions.ship import ShipNotFoundError
from app.domain.exceptions.zone import ZoneNotFoundError
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.equipment_repository import EquipmentRepository
from app.domain.services.expedition_calculator import ExpeditionCalculatorService
from app.application.dtos.zone_preview_dto import ZonePreviewDTO


class GetZonePreviewUseCase:
    def __init__(
        self,
        zone_repo: ZoneRepository,
        equipment_repo: EquipmentRepository,
    ):
        self.zone_repo = zone_repo
        self.equipment_repo = equipment_repo

    async def execute(
        self,
        player: Player,
        zone_id: UUID,
        ship_id: UUID,
    ) -> ZonePreviewDTO:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone:
            raise ZoneNotFoundError(f"Zone {zone_id} not found")

        ship = next((s for s in player.ships if s.id == ship_id), None)
        if not ship:
            raise ShipNotFoundError(f"Ship {ship_id} not found")

        equipment = await self.equipment_repo.get_by_ship_id(ship.id)

        preview = ExpeditionCalculatorService.compute_preview(
            zone=zone,
            ship=ship,
            equipment=equipment,
        )

        return ZonePreviewDTO(
            effective_fuel_cost=preview.effective_fuel_cost,
            effective_duration_seconds=preview.effective_duration_seconds,
            estimated_damage_percent=preview.estimated_damage_percent,
            risk_percent=preview.risk_percent,
            fuel_ok=preview.fuel_ok,
            artifact_bonuses=preview.artifact_bonuses,
        )
