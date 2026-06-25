from app.application.dtos.zone_dto import ZoneResponseDTO
from app.domain.repositories.zone_repository import ZoneRepository


class GetZonesUseCase:
    def __init__(self, zone_repo: ZoneRepository):
        self.zone_repo = zone_repo

    async def execute(self) -> list[ZoneResponseDTO]:
        zones = await self.zone_repo.get_all()

        return [ZoneResponseDTO.model_validate(zone) for zone in zones]
