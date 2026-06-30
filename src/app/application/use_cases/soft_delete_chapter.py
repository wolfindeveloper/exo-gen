from uuid import UUID

from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.exceptions.guide import ChapterNotFoundError


class SoftDeleteChapterUseCase:
    def __init__(self, chapter_repo: ChapterRepository):
        self.chapter_repo = chapter_repo

    async def execute(self, chapter_id: UUID, uow: UnitOfWork) -> None:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter or chapter.is_deleted():
            raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

        chapter.soft_delete()
        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
