from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.exceptions.guide import ChapterNotFoundError, ArticleNotFoundError


class ReorderChapterArticlesUseCase:
    def __init__(self, chapter_repo: ChapterRepository):
        self.chapter_repo = chapter_repo

    async def execute(self, chapter_id: UUID, article_ids: list[UUID], uow: UnitOfWork) -> None:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter or chapter.is_deleted():
            raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

        existing_ids = {a.id for a in chapter.articles}
        for idx, article_id in enumerate(article_ids):
            if article_id not in existing_ids:
                raise ArticleNotFoundError(f"Article {article_id} not in chapter")
            for article in chapter.articles:
                if article.id == article_id:
                    article.sort_order = idx
                    break

        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
