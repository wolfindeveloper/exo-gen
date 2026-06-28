import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.presentation.api.dependencies import get_db_session, get_zone_repo, get_uow
from app.domain.uow import UnitOfWork
from app.infrastructure.telegram.security import get_admin_player
from app.infrastructure.persistence.models.season_orm import SeasonORM
from app.infrastructure.persistence.models.chapter_orm import ChapterORM
from app.infrastructure.persistence.models.article_orm import ArticleORM
from app.infrastructure.persistence.models.item_orm import ItemORM

from app.application.dtos.guide_dto import (
    CreateSeasonDTO, SeasonResponseDTO,
    CreateArticleDTO, ArticleResponseDTO,
    CreateChapterDTO, ChapterResponseDTO
)
from app.application.dtos.zone_dto import CreateZoneDTO
from app.application.dtos.item_dto import CreateItemDTO, ItemResponseDTO
from app.application.use_cases.create_zone import CreateZoneUseCase
from app.domain.repositories.zone_repository import ZoneRepository

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_player)])

@router.post("/zones", status_code=201)
async def create_zone(
    dto: CreateZoneDTO,
    zone_repo: ZoneRepository = Depends(get_zone_repo),
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = CreateZoneUseCase(zone_repo=zone_repo)
    await use_case.execute(dto, uow)
    return {"status": "Zone created successfully"}

@router.post("/seasons", response_model=SeasonResponseDTO, status_code=201)
async def create_season(
    dto: CreateSeasonDTO,
    session: AsyncSession = Depends(get_db_session)
):
    # Создаем ORM-объект, а не DTO!
    new_season = SeasonORM(
        id=uuid.uuid4(),
        name=dto.name,
        description=dto.description,
        start_date=dto.start_date,
        end_date=dto.end_date,
        reward_xgen=dto.reward_xgen,
        reward_fragments=dto.reward_fragments,
        is_active=dto.is_active
    )

    session.add(new_season)
    await session.commit()
    return new_season

@router.post("/chapters", response_model=ChapterResponseDTO, status_code=201)
async def create_chapter(
    dto: CreateChapterDTO,
    session: AsyncSession = Depends(get_db_session)
):
    # 1. Сначала создаем ORM-объекты для вложенных статей
    article_orms = [
            ArticleORM(
                id=uuid.uuid4(),
                title=article_dto.title,
                content=article_dto.content,
                fragment_cost=article_dto.fragment_cost,
                trigger_event_type=article_dto.trigger_event_type,
                trigger_threshold=article_dto.trigger_threshold
                # chapter_id НЕ указываем! SQLAlchemy проставит его сам через cascade
            ) for article_dto in dto.articles
            ]   

    # 2. Создаем главу и привязываем статьи
    new_chapter = ChapterORM(
        id=uuid.uuid4(),
        name=dto.name,
        description=dto.description,
        is_secret=dto.is_secret,
        season_id=dto.season_id, # Берем из DTO (может быть None)
        reward_xgen=dto.reward_xgen,
        reward_fragments=dto.reward_fragments,
        articles=article_orms # Передаем список статей
    )

    session.add(new_chapter)
    await session.commit()
    return new_chapter

@router.post("/articles", response_model=ArticleResponseDTO, status_code=201)
async def create_article(
    dto: CreateArticleDTO,
    session: AsyncSession = Depends(get_db_session)
):

    if not dto.chapter_id:
        raise HTTPException(status_code=400, detail="chapter_id is required for standalone articles")

    new_article = ArticleORM(
        id=uuid.uuid4(),
        chapter_id=dto.chapter_id, # Требуется существующий ID главы
        title=dto.title,
        content=dto.content,
        fragment_cost=dto.fragment_cost,
        trigger_event_type=dto.trigger_event_type,
        trigger_threshold=dto.trigger_threshold
    )

    session.add(new_article)
    await session.commit()
    return new_article


@router.get("/all_seasons", response_model=list[SeasonResponseDTO])
async def get_all_seasons(
    session: AsyncSession = Depends(get_db_session)
):

    stmt = select(SeasonORM).order_by(SeasonORM.start_date.desc())

    result = await session.execute(stmt)
    seasons = result.scalars().all()

    return seasons


@router.get("/all_chapters", response_model=list[ChapterResponseDTO])
async def get_all_chapters(
    session: AsyncSession = Depends(get_db_session)
):

    stmt = select(ChapterORM).options(selectinload(ChapterORM.articles))

    result = await session.execute(stmt)
    chapters = result.scalars().all()

    return chapters


@router.get("/all_articles", response_model=list[ArticleResponseDTO])
async def get_all_articles(
    session: AsyncSession = Depends(get_db_session)
):

    stmt = select(ArticleORM).order_by(ArticleORM.title.asc())

    result = await session.execute(stmt)
    articles = result.scalars().all()

    return articles


@router.post("/items", response_model=ItemResponseDTO, status_code=201)
async def create_item(
    dto: CreateItemDTO,
    session: AsyncSession = Depends(get_db_session)
):
    # Создаем ORM-объект напрямую
    new_item = ItemORM(
        id=uuid.uuid4(),
        name=dto.name,
        description=dto.description,
        type=dto.type.value, # Enum -> Строка для БД
        rarity=dto.rarity,
        effect=dto.effect,
        is_tradable=dto.is_tradable,
        sell_price=dto.sell_price
    )
    
    session.add(new_item)
    await session.commit()
    # refresh не нужен, так как UUID мы сгенерили сами, а других дефолтов БД нет
    return new_item