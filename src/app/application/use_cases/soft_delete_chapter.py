from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.exceptions.guide import ChapterNotFoundError, ArticleHasUnlocksError


class SoftDeleteChapterUseCase:
    def __init__(
        self,
        chapter_repo: ChapterRepository,
        guide_progress_repo: GuideProgressRepository,
    ):
        self.chapter_repo = chapter_repo
        self.guide_progress_repo = guide_progress_repo

    async def execute(self, chapter_id: UUID, uow: UnitOfWork) -> None:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter or chapter.is_deleted():
            raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

        for article in chapter.articles:
            unlocked_count = await self.guide_progress_repo.count_unlocked_by_article_id(article.id)
            if unlocked_count > 0:
                raise ArticleHasUnlocksError(article.title, unlocked_count)

        chapter.soft_delete()
        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
