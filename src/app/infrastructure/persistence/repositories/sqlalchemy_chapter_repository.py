from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.domain.entities.chapter import Chapter
from app.domain.repositories.chapter_repository import ChapterRepository
from app.infrastructure.persistence.models.chapter_orm import ChapterORM
from app.infrastructure.persistence.models.article_orm import ArticleORM
from app.infrastructure.persistence.mappers import ChapterMapper



class SQLAlchemyChapterRepository(ChapterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, chapter: Chapter) -> None:
        chapter_orm = ChapterMapper.chapter_to_orm(chapter)
        await self.session.merge(chapter_orm)

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