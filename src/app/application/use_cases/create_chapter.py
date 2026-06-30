import uuid

from app.domain.entities.chapter import Chapter
from app.domain.entities.article import Article
from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.exceptions.guide import SeasonNotFoundError
from app.application.dtos.guide_dto import CreateChapterDTO


class CreateChapterUseCase:
    def __init__(self, chapter_repo: ChapterRepository, season_repo: SeasonRepository):
        self.chapter_repo = chapter_repo
        self.season_repo = season_repo

    async def execute(self, dto: CreateChapterDTO, uow: UnitOfWork) -> Chapter:
        if dto.season_id is not None:
            season = await self.season_repo.get_by_id(dto.season_id)
            if season is None:
                raise SeasonNotFoundError(str(dto.season_id))

        chapter_id = uuid.uuid4()

        articles = [
            Article(
                id=uuid.uuid4(),
                chapter_id=chapter_id,
                title=a.title,
                content=a.content,
                fragment_cost=a.fragment_cost,
                trigger_event_type=a.trigger_event_type,
                trigger_threshold=a.trigger_threshold,
            )
            for a in dto.articles
        ]

        chapter = Chapter(
            id=chapter_id,
            name=dto.name,
            description=dto.description,
            is_secret=dto.is_secret,
            season_id=dto.season_id,
            reward_xgen=dto.reward_xgen,
            reward_fragments=dto.reward_fragments,
            articles=articles,
        )

        await self.chapter_repo.save(chapter)
        await uow.commit()

        return chapter
