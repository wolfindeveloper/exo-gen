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

    async def get_all_with_articles(self) -> list[Chapter]:
        stmt = select(ChapterORM).options(selectinload(ChapterORM.articles))
        result = await self.session.execute(stmt)
        chapters_orm = result.scalars().all()

        return [ChapterMapper.chapter_to_domain(c) for c in chapters_orm]


    async def get_by_id(self, chapter_id: UUID) -> Chapter | None:
        stmt = (
            select(ChapterORM)
            .options(selectinload(ChapterORM.articles))
            .where(ChapterORM.id == chapter_id)
        )

        result = await self.session.execute(stmt)
        chapter_orm = result.scalar_one_or_none()
        if not chapter_orm:
            return None

        return ChapterMapper.chapter_to_domain(chapter_orm)

    async def get_chapter_by_article_id(self, article_id: UUID) -> Chapter | None:
        stmt = (
            select(ChapterORM)
            .options(selectinload(ChapterORM.articles))
            # .any() проверяет, есть ли в коллекции articles статья с нужным id
            .where(ChapterORM.articles.any(ArticleORM.id == article_id))
        )

        result = await self.session.execute(stmt)
        chapter_orm = result.scalar_one_or_none()

        if not chapter_orm:
            return None

        return ChapterMapper.chapter_to_domain(chapter_orm)