from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.exceptions.guide import ArticleNotFoundError, ArticleHasUnlocksError


class SoftDeleteArticleUseCase:
    def __init__(
        self,
        chapter_repo: ChapterRepository,
        guide_progress_repo: GuideProgressRepository,
    ):
        self.chapter_repo = chapter_repo
        self.guide_progress_repo = guide_progress_repo

    async def execute(self, article_id: UUID, uow: UnitOfWork) -> None:
        chapter = await self.chapter_repo.get_chapter_by_article_id(article_id)
        if not chapter:
            raise ArticleNotFoundError(f"Article {article_id} not found")

        article = next((a for a in chapter.articles if a.id == article_id), None)
        if not article or article.is_deleted():
            raise ArticleNotFoundError(f"Article {article_id} not found")

        unlocked_count = await self.guide_progress_repo.count_unlocked_by_article_id(article_id)
        if unlocked_count > 0:
            raise ArticleHasUnlocksError(article.title, unlocked_count)

        article.soft_delete()
        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
