from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.application.use_cases.get_guide import GetGuideUseCase
from app.application.use_cases.unlock_article import UnlockArticleUseCase
from app.application.use_cases.process_trigger import ProcessTriggerUseCase
from app.application.use_cases.get_leaderboard import GetLeaderboardUseCase
from app.domain.exceptions import DomainError
from app.domain.uow import UnitOfWork
from app.infrastructure.telegram.security import get_current_player
from app.domain.entities.player import Player
from app.application.dtos.guide_dto import (
    GuideResponseDTO,
    UnlockArticleDTO,
    UnlockArticleResponseDTO,
    TriggerEventDTO,
    TriggerEventResponseDTO,
    LeaderboardEntryDTO,
)


from app.presentation.api.dependencies import (
    get_player_repo,
    get_chapter_repo,
    get_season_repo,
    get_guide_progress_repo,
    get_inventory_repo,
    get_loot_box_repo,
    get_uow,
)

router = APIRouter(prefix="/guide", tags=["Guide"])


@router.get("/", response_model=GuideResponseDTO)
async def get_guide(
    current_player: Player = Depends(get_current_player),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    season_repo: SeasonRepository = Depends(get_season_repo),
    progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
):

    use_case = GetGuideUseCase(chapter_repo, season_repo, progress_repo)
    return await use_case.execute(current_player)


@router.post("/unlock", response_model=UnlockArticleResponseDTO)
async def unlock_article(
    dto: UnlockArticleDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    season_repo: SeasonRepository = Depends(get_season_repo),
    guide_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = UnlockArticleUseCase(
        player_repo,
        chapter_repo,
        season_repo,
        guide_repo,
        loot_box_service=LootBoxService(),
        loot_box_repo=loot_box_repo,
        inventory_repo=inventory_repo,
    )
    try:
        return await use_case.execute(current_player, dto.article_id, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/trigger", response_model=TriggerEventResponseDTO)
async def process_trigger(
    dto: TriggerEventDTO,
    current_player: Player = Depends(get_current_player),
    player_repo: PlayerRepository = Depends(get_player_repo),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    season_repo: SeasonRepository = Depends(get_season_repo),
    guide_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = ProcessTriggerUseCase(
        player_repo,
        chapter_repo,
        season_repo,
        guide_repo,
        loot_box_service=LootBoxService(),
        loot_box_repo=loot_box_repo,
        inventory_repo=inventory_repo,
    )
    try:
        return await use_case.execute(current_player, dto, uow)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard", response_model=list[LeaderboardEntryDTO])
async def get_leaderboard(
    season_id: UUID,  # Передаем ID сезона как query-параметр
    progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
):

    use_case = GetLeaderboardUseCase(progress_repo)
    return await use_case.execute(season_id)
