from uuid import UUID

from app.domain.entities.player import Player
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import ChapterResponseDTO, ArticleResponseDTO, GuideResponseDTO

class GetGuideUseCase:
    def __init__(
        self,
        chapter_repo: ChapterRepository,
        season_repo: SeasonRepository,
        progress_repo: GuideProgressRepository,
    ):
        self.chapter_repo = chapter_repo
        self.season_repo = season_repo
        self.progress_repo = progress_repo

    async def execute(self, player: Player) -> GuideResponseDTO:
        chapters = await self.chapter_repo.get_all_with_articles()
        unlocked_ids = await self.progress_repo.get_unlocked_articles_ids(player.id)

        chapters_dto = []
        season_cache: dict[UUID, bool] = {}

        for ch in chapters:
            if ch.season_id is not None:
                if ch.season_id not in season_cache:
                    season = await self.season_repo.get_by_id(ch.season_id)
                    season_cache[ch.season_id] = (
                        season is not None and season.is_currently_active()
                    )
                if not season_cache[ch.season_id]:
                    is_completed = await self.progress_repo.is_chapter_completed(
                        player.id, ch.id
                    )
                    if not is_completed:
                        continue

            articles_dto = []
            for art in ch.articles:
                is_unlocked = art.id in unlocked_ids
                articles_dto.append(ArticleResponseDTO(
                    id=art.id,
                    chapter_id=art.chapter_id,
                    title=art.title,
                    content=art.content if is_unlocked else None,
                    is_unlocked=is_unlocked,
                    fragment_cost=art.fragment_cost,
                    trigger_event_type=art.trigger_event_type,
                    trigger_threshold=art.trigger_threshold
                ))

            chapters_dto.append(ChapterResponseDTO(
                id=ch.id,
                name=ch.name,
                description=ch.description,
                is_secret=ch.is_secret,
                season_id=ch.season_id,
                reward_xgen=ch.reward_xgen,
                reward_fragments=ch.reward_fragments,
                articles=articles_dto
            ))

        return GuideResponseDTO(
            chapters=chapters_dto,
            player_fragments_balance=player.fragments_balance.value
        )

