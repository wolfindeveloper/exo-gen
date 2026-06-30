import uuid

from app.domain.entities.article import Article
from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.exceptions.guide import ChapterNotFoundError
from app.application.dtos.guide_dto import CreateArticleDTO


class CreateArticleUseCase:
    def __init__(self, chapter_repo: ChapterRepository):
        self.chapter_repo = chapter_repo

    async def execute(self, dto: CreateArticleDTO, uow: UnitOfWork) -> Article:
        if dto.chapter_id is None:
            raise ValueError("chapter_id is required")

        chapter = await self.chapter_repo.get_by_id(dto.chapter_id)
        if chapter is None:
            raise ChapterNotFoundError(f"Chapter with id '{dto.chapter_id}' not found")

        article = Article(
            id=uuid.uuid4(),
            chapter_id=dto.chapter_id,
            title=dto.title,
            content=dto.content,
            fragment_cost=dto.fragment_cost,
            trigger_event_type=dto.trigger_event_type,
            trigger_threshold=dto.trigger_threshold,
        )

        chapter.articles.append(article)
        await self.chapter_repo.save(chapter)
        await uow.commit()

        return article
