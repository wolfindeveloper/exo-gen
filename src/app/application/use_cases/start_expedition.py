from uuid import UUID

from app.domain.entities.player import Player
from app.application.dtos.expedition_dto import StartExpeditionDTO, ExpeditionResponseDTO
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository


class StartExpeditionUseCase:
    def __init__(self, player_repo: PlayerRepository, zone_repo: ZoneRepository, expedition_repo: ExpeditionRepository):
        self.player_repo = player_repo
        self.zone_repo = zone_repo
        self.expedition_repo = expedition_repo

    
    async def execute(self, player: Player, dto: StartExpeditionDTO) -> ExpeditionResponseDTO:
        ship = next((s for s in player.ships if s.id == dto.ship_id), None)

        if not ship:
            raise ValueError("Ship not found")
        
        zone = await self.zone_repo.get_by_id(zone_id=dto.zone_id)

        if not zone:
            raise ValueError("Zone not found")

        active_expedition = await self.expedition_repo.get_active_by_ship_id(ship_id=ship.id)

        if active_expedition:
            raise ValueError("Ship is already in expedition")
        
        new_expedition = ship.start_expedition(zone)

        await self.player_repo.save(player)
        await self.expedition_repo.save(new_expedition)

        return ExpeditionResponseDTO(
            id=new_expedition.id,
            ship_id=ship.id,
            zone_id=zone.id,
            started_at=new_expedition.started_at,
            ends_at=new_expedition.ends_at,
            status=new_expedition.status.value,
            remaining_tea=ship.tea_level
        )
        
