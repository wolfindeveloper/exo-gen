from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.presentation.api.dependencies import (
    get_uow, get_zone_repo, get_season_repo, get_chapter_repo,
    get_item_repo, get_loot_box_repo, get_shop_item_repo,
    get_stars_package_repo,
)
from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.exceptions import ItemNotFoundError
from app.domain.exceptions.guide import SeasonNotFoundError, ChapterNotFoundError, ArticleNotFoundError
from app.domain.exceptions.zone import ZoneNotFoundError
from app.domain.exceptions.shop import ShopItemNotFoundError
from app.domain.exceptions.stars import StarsPackageNotFoundError
from app.domain.exceptions.loot_box import LootBoxConfigNotFoundError
from app.infrastructure.telegram.security import get_admin_player

from app.application.dtos.guide_dto import (
    CreateSeasonDTO, SeasonResponseDTO,
    CreateArticleDTO, ArticleResponseDTO,
    CreateChapterDTO, ChapterResponseDTO,
)
from app.application.dtos.zone_dto import CreateZoneDTO, ZoneResponseDTO
from app.application.dtos.item_dto import CreateItemDTO, ItemResponseDTO
from app.application.dtos.shop_dto import ShopItemResponseDTO
from app.application.dtos.stars_dto import StarsPackageResponseDTO
from app.application.dtos.admin_dto import (
    UpdateZoneDTO, UpdateItemDTO, UpdateChapterDTO,
    UpdateArticleDTO, UpdateSeasonDTO, UpdateLootBoxConfigDTO,
    UpdateShopItemDTO, UpdateStarsPackageDTO, LootBoxConfigResponseDTO,
)
from app.application.use_cases.create_zone import CreateZoneUseCase
from app.application.use_cases.create_season import CreateSeasonUseCase
from app.application.use_cases.create_chapter import CreateChapterUseCase
from app.application.use_cases.create_article import CreateArticleUseCase
from app.application.use_cases.create_item import CreateItemUseCase
from app.application.use_cases.update_zone import UpdateZoneUseCase
from app.application.use_cases.update_item import UpdateItemUseCase
from app.application.use_cases.update_chapter import UpdateChapterUseCase
from app.application.use_cases.update_article import UpdateArticleUseCase
from app.application.use_cases.update_season import UpdateSeasonUseCase
from app.application.use_cases.update_loot_box_config import UpdateLootBoxConfigUseCase
from app.application.use_cases.update_shop_item import UpdateShopItemUseCase
from app.application.use_cases.update_stars_package import UpdateStarsPackageUseCase
from app.application.use_cases.soft_delete_zone import SoftDeleteZoneUseCase
from app.application.use_cases.soft_delete_item import SoftDeleteItemUseCase
from app.application.use_cases.soft_delete_chapter import SoftDeleteChapterUseCase
from app.application.use_cases.soft_delete_article import SoftDeleteArticleUseCase
from app.application.use_cases.soft_delete_season import SoftDeleteSeasonUseCase
from app.application.use_cases.soft_delete_loot_box_config import SoftDeleteLootBoxConfigUseCase
from app.application.use_cases.soft_delete_shop_item import SoftDeleteShopItemUseCase
from app.application.use_cases.soft_delete_stars_package import SoftDeleteStarsPackageUseCase

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_player)])


# ─── CREATE ────────────────────────────────────────────────────


@router.post("/zones", status_code=201)
async def create_zone(
    dto: CreateZoneDTO,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateZoneUseCase(zone_repo=zone_repo)
    await use_case.execute(dto, uow)
    return {"status": "Zone created successfully"}


@router.post("/seasons", response_model=SeasonResponseDTO, status_code=201)
async def create_season(
    dto: CreateSeasonDTO,
    season_repo: SeasonRepository = Depends(get_season_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateSeasonUseCase(season_repo=season_repo)
    season = await use_case.execute(dto, uow)
    return season


@router.post("/chapters", response_model=ChapterResponseDTO, status_code=201)
async def create_chapter(
    dto: CreateChapterDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    season_repo: SeasonRepository = Depends(get_season_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = CreateChapterUseCase(chapter_repo=chapter_repo, season_repo=season_repo)
        chapter = await use_case.execute(dto, uow)
        return chapter
    except SeasonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/articles", response_model=ArticleResponseDTO, status_code=201)
async def create_article(
    dto: CreateArticleDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    if not dto.chapter_id:
        raise HTTPException(status_code=400, detail="chapter_id is required")
    try:
        use_case = CreateArticleUseCase(chapter_repo=chapter_repo)
        article = await use_case.execute(dto, uow)
        return article
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/items", response_model=ItemResponseDTO, status_code=201)
async def create_item(
    dto: CreateItemDTO,
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateItemUseCase(item_repo=item_repo)
    item = await use_case.execute(dto, uow)
    return item


# ─── READ ──────────────────────────────────────────────────────


@router.get("/zones", response_model=list[ZoneResponseDTO])
async def get_all_zones(
    zone_repo: ZoneRepository = Depends(get_zone_repo),
):
    return await zone_repo.get_all()


@router.get("/seasons", response_model=list[SeasonResponseDTO])
async def get_all_seasons(
    season_repo: SeasonRepository = Depends(get_season_repo),
):
    return await season_repo.get_all()


@router.get("/chapters", response_model=list[ChapterResponseDTO])
async def get_all_chapters(
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
):
    return await chapter_repo.get_all_with_articles()


@router.get("/articles", response_model=list[ArticleResponseDTO])
async def get_all_articles(
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
):
    chapters = await chapter_repo.get_all_with_articles()
    return [article for chapter in chapters for article in chapter.articles]


@router.get("/items", response_model=list[ItemResponseDTO])
async def get_all_items(
    item_repo: ItemRepository = Depends(get_item_repo),
):
    return await item_repo.get_all()


# ─── UPDATE ────────────────────────────────────────────────────


@router.patch("/zones/{zone_id}", response_model=ZoneResponseDTO)
async def update_zone(
    zone_id: UUID,
    dto: UpdateZoneDTO,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateZoneUseCase(zone_repo=zone_repo)
        return await use_case.execute(zone_id, dto, uow)
    except ZoneNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/seasons/{season_id}", response_model=SeasonResponseDTO)
async def update_season(
    season_id: UUID,
    dto: UpdateSeasonDTO,
    season_repo: SeasonRepository = Depends(get_season_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateSeasonUseCase(season_repo=season_repo)
        return await use_case.execute(season_id, dto, uow)
    except SeasonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/chapters/{chapter_id}", response_model=ChapterResponseDTO)
async def update_chapter(
    chapter_id: UUID,
    dto: UpdateChapterDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateChapterUseCase(chapter_repo=chapter_repo)
        return await use_case.execute(chapter_id, dto, uow)
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/articles/{article_id}", response_model=ArticleResponseDTO)
async def update_article(
    article_id: UUID,
    dto: UpdateArticleDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateArticleUseCase(chapter_repo=chapter_repo)
        return await use_case.execute(article_id, dto, uow)
    except ArticleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/items/{item_id}", response_model=ItemResponseDTO)
async def update_item(
    item_id: UUID,
    dto: UpdateItemDTO,
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateItemUseCase(item_repo=item_repo)
        return await use_case.execute(item_id, dto, uow)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/loot-boxes/{config_id}", response_model=LootBoxConfigResponseDTO)
async def update_loot_box_config(
    config_id: UUID,
    dto: UpdateLootBoxConfigDTO,
    config_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateLootBoxConfigUseCase(config_repo=config_repo)
        return await use_case.execute(config_id, dto, uow)
    except LootBoxConfigNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/shop-items/{shop_item_id}", response_model=ShopItemResponseDTO)
async def update_shop_item(
    shop_item_id: UUID,
    dto: UpdateShopItemDTO,
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateShopItemUseCase(shop_item_repo=shop_item_repo)
        return await use_case.execute(shop_item_id, dto, uow)
    except ShopItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/stars-packages/{package_id}", response_model=StarsPackageResponseDTO)
async def update_stars_package(
    package_id: UUID,
    dto: UpdateStarsPackageDTO,
    package_repo: StarsPackageRepository = Depends(get_stars_package_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateStarsPackageUseCase(package_repo=package_repo)
        return await use_case.execute(package_id, dto, uow)
    except StarsPackageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── SOFT DELETE ───────────────────────────────────────────────


@router.delete("/zones/{zone_id}", status_code=204)
async def delete_zone(
    zone_id: UUID,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteZoneUseCase(zone_repo=zone_repo)
        await use_case.execute(zone_id, uow)
    except ZoneNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/seasons/{season_id}", status_code=204)
async def delete_season(
    season_id: UUID,
    season_repo: SeasonRepository = Depends(get_season_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteSeasonUseCase(season_repo=season_repo)
        await use_case.execute(season_id, uow)
    except SeasonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    chapter_id: UUID,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteChapterUseCase(chapter_repo=chapter_repo)
        await use_case.execute(chapter_id, uow)
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(
    article_id: UUID,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteArticleUseCase(chapter_repo=chapter_repo)
        await use_case.execute(article_id, uow)
    except ArticleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteItemUseCase(item_repo=item_repo)
        await use_case.execute(item_id, uow)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/loot-boxes/{config_id}", status_code=204)
async def delete_loot_box_config(
    config_id: UUID,
    config_repo: LootBoxRepository = Depends(get_loot_box_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteLootBoxConfigUseCase(config_repo=config_repo)
        await use_case.execute(config_id, uow)
    except LootBoxConfigNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/shop-items/{shop_item_id}", status_code=204)
async def delete_shop_item(
    shop_item_id: UUID,
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteShopItemUseCase(shop_item_repo=shop_item_repo)
        await use_case.execute(shop_item_id, uow)
    except ShopItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/stars-packages/{package_id}", status_code=204)
async def delete_stars_package(
    package_id: UUID,
    package_repo: StarsPackageRepository = Depends(get_stars_package_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteStarsPackageUseCase(package_repo=package_repo)
        await use_case.execute(package_id, uow)
    except StarsPackageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
