from uuid import UUID

from app.domain.entities.chapter import Chapter
from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.exceptions.guide import ChapterNotFoundError
from app.application.dtos.admin_dto import UpdateChapterDTO


class UpdateChapterUseCase:
    def __init__(self, chapter_repo: ChapterRepository):
        self.chapter_repo = chapter_repo

    async def execute(self, chapter_id: UUID, dto: UpdateChapterDTO, uow: UnitOfWork) -> Chapter:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter or chapter.is_deleted():
            raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

        chapter.update(**dto.model_dump(exclude_none=True))

        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
        return chapter
