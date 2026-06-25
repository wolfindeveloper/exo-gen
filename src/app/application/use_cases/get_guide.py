from app.domain.entities.player import Player
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import ChapterResponseDTO, ArticleResponseDTO, GuideResponseDTO

class GetGuideUseCase:
    def __init__(self, chapter_repo: ChapterRepository, progress_repo: GuideProgressRepository):
        self.chapter_repo = chapter_repo
        self.progress_repo = progress_repo

    async def execute(self, player: Player) -> GuideResponseDTO:
        chapters = await self.chapter_repo.get_all_with_articles()
        unlocked_ids = await self.progress_repo.get_unlocked_articles_ids(player.id)

        chapters_dto = []
        for ch in chapters:
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
            player_fragments_balance=player.fragments_balance
        )

