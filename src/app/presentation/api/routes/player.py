from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos.player_dto import CreatePlayerDTO
from app.application.dtos.player_response_dto import PlayerResponseDTO
from app.application.use_cases.create_player import CreatePlayerUseCase
from app.application.use_cases.get_player import GetPlayerUseCase
from app.application.use_cases.process_daily_login import ProcessDailyLoginUseCase
from app.domain.repositories.player_repository import PlayerRepository
from app.presentation.api.dependencies import get_player_repo

router = APIRouter(prefix="/players", tags=["Players"])

@router.post("/register", status_code=201)
async def register_player(
    dto: CreatePlayerDTO, 
    player_repo: PlayerRepository = Depends(get_player_repo)
):
    use_case = CreatePlayerUseCase(player_repo=player_repo)
    player = await use_case.execute(dto)
    # Здесь мы возвращаем DTO или просто данные, чтобы не светить внутренние dataclass/ORM
    return {"id": str(player.id), "telegram_id": player.telegram_id, "ships": len(player.ships)}


@router.get("/telegram_id", response_model=PlayerResponseDTO)
async def get_player(
    telegram_id: int,
    player_repo: PlayerRepository = Depends(get_player_repo)
):

    use_case = GetPlayerUseCase(player_repo=player_repo)
    player = await use_case.execute(telegram_id=telegram_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player


@router.post("/{telegram_id}/daily-login")
async def daily_login(
    telegram_id: int,
    player_repo: PlayerRepository = Depends(get_player_repo)
):

    use_case = ProcessDailyLoginUseCase(player_repo=player_repo)
    try:
        result = await use_case.execute(telegram_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))