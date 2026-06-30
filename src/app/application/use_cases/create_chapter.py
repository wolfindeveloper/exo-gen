import uuid

from app.domain.entities.chapter import Chapter
from app.domain.uow import UnitOfWork
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions.guide import SeasonNotFoundError, ChapterNotFoundError
from app.domain.exceptions import ItemNotFoundError
from app.application.dtos.guide_dto import CreateChapterDTO


class CreateChapterUseCase:
    def __init__(
        self,
        chapter_repo: ChapterRepository,
        season_repo: SeasonRepository,
        item_repo: ItemRepository,
    ):
        self.chapter_repo = chapter_repo
        self.season_repo = season_repo
        self.item_repo = item_repo

    async def execute(self, dto: CreateChapterDTO, uow: UnitOfWork) -> Chapter:
        if dto.season_id is not None:
            season = await self.season_repo.get_by_id(dto.season_id)
            if season is None:
                raise SeasonNotFoundError(str(dto.season_id))

        if dto.reward_items:
            item_ids = [r.item_id for r in dto.reward_items]
            existing = await self.item_repo.get_by_ids(item_ids)
            existing_ids = {it.id for it in existing if not it.is_deleted()}
            for r in dto.reward_items:
                if r.item_id not in existing_ids:
                    raise ItemNotFoundError(r.item_id)

        chapter_id = uuid.uuid4()

        articles = []
        if dto.article_ids:
            found = await self.chapter_repo.get_articles_by_ids(dto.article_ids)
            found_map = {a.id: a for a in found}
            for idx, aid in enumerate(dto.article_ids):
                article = found_map.get(aid)
                if not article:
                    raise ChapterNotFoundError(f"Article {aid} not found")
                article.chapter_id = chapter_id
                article.sort_order = idx
                articles.append(article)

        chapter = Chapter(
            id=chapter_id,
            name=dto.name,
            description=dto.description,
            is_secret=dto.is_secret,
            season_id=dto.season_id,
            reward_xgen=dto.reward_xgen,
            reward_fragments=dto.reward_fragments,
            reward_items=[r.model_dump() for r in dto.reward_items],
            articles=articles,
        )

        await self.chapter_repo.save(chapter)
        await uow.commit()

        return chapter
