from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.presentation.api.dependencies import (
    get_uow, get_zone_repo, get_season_repo, get_chapter_repo,
    get_item_repo, get_inventory_repo, get_loot_box_repo,
    get_shop_item_repo, get_purchase_repo, get_stars_package_repo,
    get_expedition_repo, get_guide_progress_repo, verify_admin,
)
from app.domain.uow import UnitOfWork
from app.domain.repositories.zone_repository import ZoneRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.shop_repository import ShopItemRepository
from app.domain.repositories.purchase_repository import PurchaseRepository
from app.domain.repositories.stars_repository import StarsPackageRepository
from app.domain.repositories.expedition_repository import ExpeditionRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.exceptions import ItemNotFoundError
from app.domain.exceptions.guide import (
    SeasonNotFoundError, ChapterNotFoundError, ArticleNotFoundError,
    SeasonActiveError, SeasonHasProgressError, ArticleHasUnlocksError,
)
from app.domain.exceptions.zone import ZoneNotFoundError, ZoneHasActiveExpeditionsError
from app.domain.exceptions.shop import ShopItemNotFoundError
from app.domain.exceptions.stars import StarsPackageNotFoundError
from app.domain.exceptions.loot_box import LootBoxConfigNotFoundError
from app.domain.exceptions.item import (
    ItemInUseInInventoryError,
    ItemUsedInActiveZoneError,
    ItemListedInShopError,
)

from app.application.dtos.guide_dto import (
    CreateSeasonDTO, SeasonResponseDTO,
    CreateArticleDTO, ArticleResponseDTO,
    CreateChapterDTO, ChapterResponseDTO,
)
from app.application.dtos.zone_dto import CreateZoneDTO, ZoneResponseDTO
from app.application.dtos.item_dto import CreateItemDTO, ItemResponseDTO
from app.application.dtos.shop_dto import (
    ShopItemResponseDTO,
    ShopItemWithAnalyticsDTO,
    ShopItemAnalyticsDTO,
)
from app.application.dtos.stars_dto import StarsPackageResponseDTO
from app.application.dtos.admin_dto import (
    UpdateZoneDTO, UpdateItemDTO, UpdateChapterDTO,
    UpdateArticleDTO, UpdateSeasonDTO, UpdateLootBoxConfigDTO,
    UpdateShopItemDTO, UpdateStarsPackageDTO, LootBoxConfigResponseDTO,
    PaginationParams, PaginatedResponseDTO,
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
from app.application.use_cases.simulate_zone_loot import SimulateZoneLootUseCase as SimulateZoneLoot
from app.application.use_cases.simulate_loot_box import SimulateLootBoxUseCase as SimulateLootBox
from app.application.use_cases.get_shop_item_analytics import GetShopItemAnalyticsUseCase as GetShopItemAnalytics
from app.application.use_cases.reorder_chapter_articles import ReorderChapterArticlesUseCase as ReorderChapterArticles
from app.application.dtos.simulation_dto import (
    SimulateLootRequestDTO,
    LootSimulationResultDTO,
    LootBoxSimulationResultDTO,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── CREATE ────────────────────────────────────────────────────


@router.post("/zones", status_code=201)
async def create_zone(
    admin_id: int = Depends(verify_admin),
    dto: CreateZoneDTO,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateZoneUseCase(zone_repo=zone_repo)
    await use_case.execute(dto, uow)
    return {"status": "Zone created successfully"}


@router.post("/seasons", response_model=SeasonResponseDTO, status_code=201)
async def create_season(
    admin_id: int = Depends(verify_admin),
    dto: CreateSeasonDTO,
    season_repo: SeasonRepository = Depends(get_season_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateSeasonUseCase(season_repo=season_repo)
    season = await use_case.execute(dto, uow)
    return season


@router.post("/chapters", response_model=ChapterResponseDTO, status_code=201)
async def create_chapter(
    admin_id: int = Depends(verify_admin),
    dto: CreateChapterDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    season_repo: SeasonRepository = Depends(get_season_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = CreateChapterUseCase(
            chapter_repo=chapter_repo,
            season_repo=season_repo,
            item_repo=item_repo,
        )
        chapter = await use_case.execute(dto, uow)
        return chapter
    except SeasonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/articles", response_model=ArticleResponseDTO, status_code=201)
async def create_article(
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
    dto: CreateItemDTO,
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = CreateItemUseCase(item_repo=item_repo)
    item = await use_case.execute(dto, uow)
    return item


# ─── READ ──────────────────────────────────────────────────────


@router.get("/zones", response_model=PaginatedResponseDTO[ZoneResponseDTO])
async def get_all_zones(
    admin_id: int = Depends(verify_admin),
    pagination: PaginationParams = Depends(),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
):
    zones, total = await zone_repo.get_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        search=pagination.search,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    return PaginatedResponseDTO(
        items=[ZoneResponseDTO.model_validate(z) for z in zones],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=-(-total // pagination.page_size),
    )


@router.post("/zones/{zone_id}/simulate-loot", response_model=list[LootSimulationResultDTO])
async def simulate_zone_loot(
    admin_id: int = Depends(verify_admin),
    zone_id: UUID,
    request: SimulateLootRequestDTO,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
):
    try:
        use_case = SimulateZoneLootUseCase(zone_repo=zone_repo, item_repo=item_repo)
        return await use_case.execute(zone_id, request.count)
    except ZoneNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/seasons", response_model=PaginatedResponseDTO[SeasonResponseDTO])
async def get_all_seasons(
    admin_id: int = Depends(verify_admin),
    pagination: PaginationParams = Depends(),
    season_repo: SeasonRepository = Depends(get_season_repo),
):
    seasons, total = await season_repo.get_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        search=pagination.search,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    return PaginatedResponseDTO(
        items=[SeasonResponseDTO.model_validate(s) for s in seasons],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=-(-total // pagination.page_size),
    )


@router.get("/chapters", response_model=PaginatedResponseDTO[ChapterResponseDTO])
async def get_all_chapters(
    admin_id: int = Depends(verify_admin),
    pagination: PaginationParams = Depends(),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
):
    chapters, total = await chapter_repo.get_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        search=pagination.search,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    return PaginatedResponseDTO(
        items=[ChapterResponseDTO.model_validate(c) for c in chapters],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=-(-total // pagination.page_size),
    )


@router.get("/articles", response_model=PaginatedResponseDTO[ArticleResponseDTO])
async def get_all_articles(
    admin_id: int = Depends(verify_admin),
    pagination: PaginationParams = Depends(),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
):
    articles, total = await chapter_repo.get_paginated_articles(
        page=pagination.page,
        page_size=pagination.page_size,
        search=pagination.search,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    return PaginatedResponseDTO(
        items=[ArticleResponseDTO.model_validate(a) for a in articles],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=-(-total // pagination.page_size),
    )


@router.get("/items", response_model=PaginatedResponseDTO[ItemResponseDTO])
async def get_all_items(
    admin_id: int = Depends(verify_admin),
    pagination: PaginationParams = Depends(),
    item_repo: ItemRepository = Depends(get_item_repo),
):
    items, total = await item_repo.get_paginated(
        page=pagination.page,
        page_size=pagination.page_size,
        search=pagination.search,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    return PaginatedResponseDTO(
        items=[ItemResponseDTO.model_validate(i) for i in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=-(-total // pagination.page_size),
    )


# ─── UPDATE ────────────────────────────────────────────────────


@router.patch("/zones/{zone_id}", response_model=ZoneResponseDTO)
async def update_zone(
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
    chapter_id: UUID,
    dto: UpdateChapterDTO,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = UpdateChapterUseCase(chapter_repo=chapter_repo, item_repo=item_repo)
        return await use_case.execute(chapter_id, dto, uow)
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/chapters/{chapter_id}/reorder-articles", status_code=204)
async def reorder_chapter_articles(
    admin_id: int = Depends(verify_admin),
    chapter_id: UUID,
    article_ids: list[UUID],
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = ReorderChapterArticlesUseCase(chapter_repo=chapter_repo)
        await use_case.execute(chapter_id, article_ids, uow)
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ArticleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/articles/{article_id}", response_model=ArticleResponseDTO)
async def update_article(
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
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


@router.post("/loot-boxes/{box_id}/simulate", response_model=list[LootBoxSimulationResultDTO])
async def simulate_loot_box(
    admin_id: int = Depends(verify_admin),
    box_id: UUID,
    request: SimulateLootRequestDTO,
    loot_box_repo: LootBoxRepository = Depends(get_loot_box_repo),
    item_repo: ItemRepository = Depends(get_item_repo),
):
    try:
        use_case = SimulateLootBoxUseCase(loot_box_repo=loot_box_repo, item_repo=item_repo)
        return await use_case.execute(box_id, request.count)
    except LootBoxConfigNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/shop-items", response_model=list[ShopItemWithAnalyticsDTO])
async def get_all_shop_items(
    admin_id: int = Depends(verify_admin),
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    purchase_repo: PurchaseRepository = Depends(get_purchase_repo),
):
    items = await shop_item_repo.get_all()
    use_case = GetShopItemAnalyticsUseCase(
        shop_item_repo=shop_item_repo,
        purchase_repo=purchase_repo,
    )
    results = []
    for item in items:
        analytics_result = await use_case.execute(item.id)
        results.append(
            ShopItemWithAnalyticsDTO(
                id=item.id,
                item_id=item.item_id,
                price_xgen=item.price_xgen,
                daily_limit=item.daily_limit,
                stock_limit=item.stock_limit,
                is_active=item.is_active,
                analytics=ShopItemAnalyticsDTO(
                    total_purchases=analytics_result.total_purchases,
                    today_purchases=analytics_result.today_purchases,
                    revenue_xgen=analytics_result.revenue_xgen,
                ),
            )
        )
    return results


@router.get("/shop-items/{item_id}/analytics")
async def get_shop_analytics(
    item_id: UUID,
    admin_id: int = Depends(verify_admin),
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    purchase_repo: PurchaseRepository = Depends(get_purchase_repo),
):
    use_case = GetShopItemAnalytics(
        shop_item_repo=shop_item_repo,
        purchase_repo=purchase_repo,
    )
    result = await use_case.execute(item_id)
    return result


@router.patch("/shop-items/{shop_item_id}", response_model=ShopItemResponseDTO)
async def update_shop_item(
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
    zone_id: UUID,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteZoneUseCase(zone_repo=zone_repo, expedition_repo=expedition_repo)
        await use_case.execute(zone_id, uow)
    except ZoneNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ZoneHasActiveExpeditionsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/seasons/{season_id}", status_code=204)
async def delete_season(
    admin_id: int = Depends(verify_admin),
    season_id: UUID,
    season_repo: SeasonRepository = Depends(get_season_repo),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    guide_progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteSeasonUseCase(
            season_repo=season_repo,
            chapter_repo=chapter_repo,
            guide_progress_repo=guide_progress_repo,
        )
        await use_case.execute(season_id, uow)
    except SeasonNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SeasonActiveError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except SeasonHasProgressError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    admin_id: int = Depends(verify_admin),
    chapter_id: UUID,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    guide_progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteChapterUseCase(
            chapter_repo=chapter_repo,
            guide_progress_repo=guide_progress_repo,
        )
        await use_case.execute(chapter_id, uow)
    except ChapterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ArticleHasUnlocksError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(
    admin_id: int = Depends(verify_admin),
    article_id: UUID,
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    guide_progress_repo: GuideProgressRepository = Depends(get_guide_progress_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteArticleUseCase(
            chapter_repo=chapter_repo,
            guide_progress_repo=guide_progress_repo,
        )
        await use_case.execute(article_id, uow)
    except ArticleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ArticleHasUnlocksError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    admin_id: int = Depends(verify_admin),
    item_id: UUID,
    item_repo: ItemRepository = Depends(get_item_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    shop_item_repo: ShopItemRepository = Depends(get_shop_item_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteItemUseCase(
            item_repo=item_repo,
            inventory_repo=inventory_repo,
            zone_repo=zone_repo,
            shop_item_repo=shop_item_repo,
        )
        await use_case.execute(item_id, uow)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ItemInUseInInventoryError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ItemUsedInActiveZoneError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ItemListedInShopError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/loot-boxes/{config_id}", status_code=204)
async def delete_loot_box_config(
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
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
    admin_id: int = Depends(verify_admin),
    package_id: UUID,
    package_repo: StarsPackageRepository = Depends(get_stars_package_repo),
    uow: UnitOfWork = Depends(get_uow),
):
    try:
        use_case = SoftDeleteStarsPackageUseCase(package_repo=package_repo)
        await use_case.execute(package_id, uow)
    except StarsPackageNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
