import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.entities.guide_progress import (
    UnlockedArticle,
    ArticleTriggerProgress,
    ChapterCompletion,
)
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.season_repository import SeasonRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.exceptions.guide import SeasonExpiredError
from app.domain.services.loot_box_service import LootBoxService
from app.application.dtos.guide_dto import TriggerEventDTO, TriggerEventResponseDTO
from app.domain.events.player_events import ArticleUnlockedEvent, ChapterCompletedEvent
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


logger = logging.getLogger(__name__)


class ProcessTriggerUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        chapter_repo: ChapterRepository,
        season_repo: SeasonRepository,
        guide_repo: GuideProgressRepository,
        loot_box_service: LootBoxService,
        loot_box_repo: LootBoxRepository,
        inventory_repo: InventoryRepository,
        item_repo: ItemRepository,
    ):
        self.player_repo = player_repo
        self.chapter_repo = chapter_repo
        self.season_repo = season_repo
        self.guide_repo = guide_repo
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo
        self.item_repo = item_repo

    async def execute(
        self, player: Player, dto: TriggerEventDTO, uow: UnitOfWork
    ) -> TriggerEventResponseDTO:
        chapters = await self.chapter_repo.get_all_with_articles()

        newly_unlocked_titles = []
        player_state_changed = False
        box_opened = False
        box_xgen = 0
        box_fragments = 0
        box_items: list[dict] = []
        season_cache: dict[UUID, bool] = {}

        for chapter in chapters:
            triggered_articles = [
                art
                for art in chapter.articles
                if art.trigger_event_type == dto.event_type
            ]

            if not triggered_articles:
                continue

            for article in triggered_articles:
                is_unlocked = await self.guide_repo.is_article_unlocked(
                    player.id, article.id
                )
                if is_unlocked:
                    continue

                progress = await self.guide_repo.get_trigger_progress(
                    player.id, article.id
                )
                if not progress:
                    progress = ArticleTriggerProgress(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        current_count=0,
                    )

                threshold_reached = progress.increment(article.trigger_threshold)

                if threshold_reached:
                    if chapter.season_id is not None:
                        if chapter.season_id not in season_cache:
                            season = await self.season_repo.get_by_id(chapter.season_id)
                            season_cache[chapter.season_id] = (
                                season is not None and season.is_currently_active()
                            )
                        if not season_cache[chapter.season_id]:
                            raise SeasonExpiredError(chapter.name)
                    now = datetime.now(timezone.utc)
                    unlocked = UnlockedArticle(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        unlocked_at=now,
                    )
                    await self.guide_repo.save_unlocked_article(unlocked)
                    newly_unlocked_titles.append(article.title)

                    player.register_event(
                        ArticleUnlockedEvent(
                            occurred_at=now,
                            player_id=player.id,
                            telegram_id=player.telegram_id,
                            article_id=article.id,
                            chapter_id=chapter.id,
                        )
                    )

                    unlocked_ids = await self.guide_repo.get_unlocked_articles_ids(
                        player.id
                    )
                    if chapter.check_completion(unlocked_ids):
                        is_completed = await self.guide_repo.is_chapter_completed(
                            player.id, chapter.id
                        )
                        if not is_completed:
                            player.add_xgen(chapter.reward_xgen)
                            player.add_fragments(chapter.reward_fragments)
                            player_state_changed = True

                            completion = ChapterCompletion(
                                id=uuid4(),
                                player_id=player.id,
                                chapter_id=chapter.id,
                                completed_at=now,
                            )
                            await self.guide_repo.save_chapter_completion(completion)

                            player.register_event(
                                ChapterCompletedEvent(
                                    occurred_at=now,
                                    player_id=player.id,
                                    telegram_id=player.telegram_id,
                                    chapter_id=chapter.id,
                                    xgen_rewarded=chapter.reward_xgen,
                                    fragments_rewarded=chapter.reward_fragments,
                                )
                            )

                            open_box_uc = OpenLootBoxUseCase(
                                self.loot_box_service,
                                self.loot_box_repo,
                                self.inventory_repo,
                                self.item_repo,
                            )
                            chapter_loot = await open_box_uc.execute(
                                player, LootBoxType.CHAPTER_REWARD, uow
                            )
                            box_opened = True
                            box_xgen += chapter_loot.xgen_earned
                            box_fragments += chapter_loot.fragments_earned
                            box_items.extend(chapter_loot.items_earned)

                await self.guide_repo.save_trigger_progress(progress)

        if player_state_changed:
            uow.track(player)
            await self.player_repo.save(player)

        await uow.commit()

        return TriggerEventResponseDTO(
            newly_unlocked_articles=newly_unlocked_titles,
            box_opened=box_opened,
            box_xgen=box_xgen,
            box_fragments=box_fragments,
            box_items=box_items,
        )
