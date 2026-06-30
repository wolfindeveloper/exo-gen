from uuid import UUID

from app.domain.entities.chapter import Chapter
from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions import ItemNotFoundError
from app.domain.exceptions.guide import ChapterNotFoundError
from app.application.dtos.admin_dto import UpdateChapterDTO


class UpdateChapterUseCase:
    def __init__(
        self,
        chapter_repo: ChapterRepository,
        item_repo: ItemRepository,
    ):
        self.chapter_repo = chapter_repo
        self.item_repo = item_repo

    async def execute(self, chapter_id: UUID, dto: UpdateChapterDTO, uow: UnitOfWork) -> Chapter:
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not chapter or chapter.is_deleted():
            raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

        data = dto.model_dump(exclude_none=True)
        if "reward_items" in data:
            reward_items = data["reward_items"]
            if reward_items is not None:
                item_ids = [r["item_id"] for r in reward_items]
                existing = await self.item_repo.get_by_ids(item_ids)
                existing_ids = {it.id for it in existing if not it.is_deleted()}
                for r in reward_items:
                    if r["item_id"] not in existing_ids:
                        raise ItemNotFoundError(r["item_id"])
                data["reward_items"] = [
                    {"item_id": str(r["item_id"]), "quantity": r["quantity"]}
                    for r in reward_items
                ]

        chapter.update(**data)

        uow.track(chapter)
        await self.chapter_repo.save(chapter)
        await uow.commit()
        return chapter
