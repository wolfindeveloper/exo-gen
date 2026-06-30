from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.domain.entities.article import Article
from app.domain.entities.chapter import Chapter
from app.domain.repositories.chapter_repository import ChapterRepository
from app.infrastructure.persistence.models.chapter_orm import ChapterORM
from app.infrastructure.persistence.models.article_orm import ArticleORM
from app.infrastructure.persistence.mappers import ChapterMapper, ArticleMapper

_CHAPTER_SORT_WHITELIST = {"name", "reward_xgen", "reward_fragments"}
_ARTICLE_SORT_WHITELIST = {"title", "fragment_cost"}


class SQLAlchemyChapterRepository(ChapterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, chapter: Chapter) -> None:
        chapter_orm = ChapterMapper.chapter_to_orm(chapter)
        await self.session.merge(chapter_orm)

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Chapter], int]:
        base = select(ChapterORM).where(ChapterORM.deleted_at.is_(None))

        if search:
            base = base.where(ChapterORM.name.ilike(f"%{search}%"))

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        if sort_by in _CHAPTER_SORT_WHITELIST:
            column = getattr(ChapterORM, sort_by)
            base = base.order_by(column.desc() if sort_order == "desc" else column.asc())

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)

        result = await self.session.execute(base)
        orms = result.scalars().all()
        return [ChapterMapper.chapter_to_domain(o) for o in orms], total

    async def get_paginated_articles(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
    ) -> tuple[list[Article], int]:
        base = select(ArticleORM).where(ArticleORM.deleted_at.is_(None))

        if search:
            base = base.where(ArticleORM.title.ilike(f"%{search}%"))

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()

        if sort_by in _ARTICLE_SORT_WHITELIST:
            column = getattr(ArticleORM, sort_by)
            base = base.order_by(column.desc() if sort_order == "desc" else column.asc())

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)

        result = await self.session.execute(base)
        orms = result.scalars().all()
        return [ArticleMapper.article_to_domain(o) for o in orms], total

    async def get_by_season_id(self, season_id: UUID) -> list[Chapter]:
        stmt = (
            select(ChapterORM)
            .where(ChapterORM.season_id == season_id)
            .where(ChapterORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [ChapterMapper.chapter_to_domain(o) for o in orms]

    async def get_all_with_articles(self) -> list[Chapter]:
        stmt = (
            select(ChapterORM)
            .options(selectinload(ChapterORM.articles))
            .where(ChapterORM.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        chapters_orm = result.scalars().all()

        chapters = [ChapterMapper.chapter_to_domain(c) for c in chapters_orm]
        for chapter in chapters:
            chapter.articles = [a for a in chapter.articles if a.deleted_at is None]
        return chapters

    async def get_by_id(self, chapter_id: UUID) -> Chapter | None:
        stmt = (
            select(ChapterORM)
            .options(selectinload(ChapterORM.articles))
            .where(ChapterORM.id == chapter_id)
            .where(ChapterORM.deleted_at.is_(None))
        )

        result = await self.session.execute(stmt)
        chapter_orm = result.scalar_one_or_none()
        if not chapter_orm:
            return None

        chapter = ChapterMapper.chapter_to_domain(chapter_orm)
        chapter.articles = [a for a in chapter.articles if a.deleted_at is None]
        return chapter

    async def get_chapter_by_article_id(self, article_id: UUID) -> Chapter | None:
        stmt = (
            select(ChapterORM)
            .options(selectinload(ChapterORM.articles))
            .where(ChapterORM.articles.any(ArticleORM.id == article_id))
            .where(ChapterORM.deleted_at.is_(None))
        )

        result = await self.session.execute(stmt)
        chapter_orm = result.scalar_one_or_none()

        if not chapter_orm:
            return None

        chapter = ChapterMapper.chapter_to_domain(chapter_orm)
        chapter.articles = [a for a in chapter.articles if a.deleted_at is None]
        return chapter