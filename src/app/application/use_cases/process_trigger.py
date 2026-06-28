import logging
from uuid import uuid4
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.entities.guide_progress import UnlockedArticle, ArticleTriggerProgress, ChapterCompletion
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import TriggerEventDTO, TriggerEventResponseDTO
from app.domain.events.player_events import ArticleUnlockedEvent, ChapterCompletedEvent


logger = logging.getLogger(__name__)


class ProcessTriggerUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        chapter_repo: ChapterRepository,
        guide_repo: GuideProgressRepository
    ):
        self.player_repo = player_repo
        self.chapter_repo = chapter_repo
        self.guide_repo = guide_repo

    async def execute(self, player: Player, dto: TriggerEventDTO, uow: UnitOfWork) -> TriggerEventResponseDTO:
        chapters = await self.chapter_repo.get_all_with_articles()

        newly_unlocked_titles = []
        player_state_changed = False

        for chapter in chapters:
            triggered_articles = [
                art for art in chapter.articles
                if art.trigger_event_type == dto.event_type
            ]

            if not triggered_articles:
                continue

            for article in triggered_articles:
                is_unlocked = await self.guide_repo.is_article_unlocked(player.id, article.id)
                if is_unlocked:
                    continue

                progress = await self.guide_repo.get_trigger_progress(player.id, article.id)
                if not progress:
                    progress = ArticleTriggerProgress(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        current_count=0
                    )

                threshold_reached = progress.increment(article.trigger_threshold)

                if threshold_reached:
                    now = datetime.now(timezone.utc)
                    unlocked = UnlockedArticle(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        unlocked_at=now
                    )
                    await self.guide_repo.save_unlocked_article(unlocked)
                    newly_unlocked_titles.append(article.title)

                    player.register_event(ArticleUnlockedEvent(
                        occurred_at=now,
                        player_id=player.id,
                        article_id=article.id,
                        chapter_id=chapter.id
                    ))

                    unlocked_ids = await self.guide_repo.get_unlocked_articles_ids(player.id)
                    if chapter.check_completion(unlocked_ids):
                        is_completed = await self.guide_repo.is_chapter_completed(player.id, chapter.id)
                        if not is_completed:
                            player.add_xgen(chapter.reward_xgen)
                            player.add_fragments(chapter.reward_fragments)
                            player_state_changed = True

                            completion = ChapterCompletion(
                                id=uuid4(),
                                player_id=player.id,
                                chapter_id=chapter.id,
                                completed_at=now
                            )
                            await self.guide_repo.save_chapter_completion(completion)

                            player.register_event(ChapterCompletedEvent(
                                occurred_at=now,
                                player_id=player.id,
                                chapter_id=chapter.id,
                                xgen_rewarded=chapter.reward_xgen,
                                fragments_rewarded=chapter.reward_fragments
                            ))

                await self.guide_repo.save_trigger_progress(progress)

        if player_state_changed:
            uow.track(player)
            await self.player_repo.save(player)

        await uow.commit()

        return TriggerEventResponseDTO(newly_unlocked_articles=newly_unlocked_titles)