from fastapi import APIRouter, Depends
from app.application.dtos.zone_dto import ZoneResponseDTO
from app.application.use_cases.get_zones import GetZonesUseCase
from app.domain.repositories.zone_repository import ZoneRepository
from app.presentation.api.dependencies import get_zone_repo

router = APIRouter(prefix="/zones", tags=["Zones"])

@router.get("/", response_model=list[ZoneResponseDTO])
async def get_zones(
    zone_repo: ZoneRepository = Depends(get_zone_repo)
):

    use_case = GetZonesUseCase(zone_repo=zone_repo)
    return await use_case.execute()