from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.value_objects.loot_box import LootBoxType
from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion
from app.domain.exceptions.guide import (
    ArticleNotFoundError,
    ChapterNotFoundError,
    ArticleAlreadyUnlockedError,
    CannotBuySecretArticleError,
)
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.loot_box_repository import LootBoxRepository
from app.domain.services.loot_box_service import LootBoxService
from app.application.dtos.guide_dto import UnlockArticleResponseDTO
from app.domain.events.player_events import ArticleUnlockedEvent, ChapterCompletedEvent
from app.application.use_cases.open_loot_box import OpenLootBoxUseCase


class UnlockArticleUseCase:
    def __init__(
        self,
        player_repo: PlayerRepository,
        chapter_repo: ChapterRepository,
        guide_repo: GuideProgressRepository,
        loot_box_service: LootBoxService | None = None,
        loot_box_repo: LootBoxRepository | None = None,
        inventory_repo: InventoryRepository | None = None,
    ):
        self.player_repo = player_repo
        self.chapter_repo = chapter_repo
        self.guide_repo = guide_repo
        self.loot_box_service = loot_box_service
        self.loot_box_repo = loot_box_repo
        self.inventory_repo = inventory_repo

    async def execute(
        self, player: Player, article_id: UUID, uow: UnitOfWork
    ) -> UnlockArticleResponseDTO:
        chapter = await self.chapter_repo.get_chapter_by_article_id(article_id)
        if not chapter:
            raise ChapterNotFoundError(f"Chapter for article {article_id} not found")

        article = next((a for a in chapter.articles if a.id == article_id), None)
        if not article:
            raise ArticleNotFoundError(f"Article {article_id} not found in chapter")

        if chapter.is_secret or article.trigger_event_type:
            raise CannotBuySecretArticleError("Cannot buy secret articles")

        if await self.guide_repo.is_article_unlocked(
            player_id=player.id, article_id=article.id
        ):
            raise ArticleAlreadyUnlockedError(f"Article {article_id} already unlocked")

        player.spend_fragments(article.fragment_cost)

        now = datetime.now(timezone.utc)
        unlocked = UnlockedArticle(
            id=uuid4(), player_id=player.id, article_id=article.id, unlocked_at=now
        )
        await self.guide_repo.save_unlocked_article(unlocked)

        player.register_event(
            ArticleUnlockedEvent(
                occurred_at=now,
                player_id=player.id,
                article_id=article.id,
                chapter_id=chapter.id,
            )
        )

        chapter_completed = False
        xgen_rewarded = 0
        fragments_rewarded = 0

        unlocked_ids = await self.guide_repo.get_unlocked_articles_ids(player.id)
        if chapter.check_completion(unlocked_ids):
            is_completed = await self.guide_repo.is_chapter_completed(
                player.id, chapter.id
            )
            if not is_completed:
                player.add_xgen(chapter.reward_xgen)
                player.add_fragments(chapter.reward_fragments)

                xgen_rewarded = chapter.reward_xgen
                fragments_rewarded = chapter.reward_fragments

                completion = ChapterCompletion(
                    id=uuid4(),
                    player_id=player.id,
                    chapter_id=chapter.id,
                    completed_at=now,
                )
                await self.guide_repo.save_chapter_completion(completion)
                chapter_completed = True

                player.register_event(
                    ChapterCompletedEvent(
                        occurred_at=now,
                        player_id=player.id,
                        chapter_id=chapter.id,
                        xgen_rewarded=xgen_rewarded,
                        fragments_rewarded=fragments_rewarded,
                    )
                )

        box_xgen = 0
        box_fragments = 0
        box_items: list[dict] = []

        if (
            chapter_completed
            and self.loot_box_service
            and self.loot_box_repo
            and self.inventory_repo
        ):
            open_box_uc = OpenLootBoxUseCase(
                self.loot_box_service, self.loot_box_repo, self.inventory_repo
            )
            loot_result = await open_box_uc.execute(
                player, LootBoxType.CHAPTER_REWARD, uow
            )
            box_xgen = loot_result.xgen_earned
            box_fragments = loot_result.fragments_earned
            box_items = loot_result.items_earned or []
            xgen_rewarded += box_xgen
            fragments_rewarded += box_fragments

        uow.track(player)
        await self.player_repo.save(player)
        await uow.commit()

        return UnlockArticleResponseDTO(
            content=article.content,
            new_fragments_balance=player.fragments_balance.value,
            chapter_completed=chapter_completed,
            xgen_rewarded=xgen_rewarded,
            fragments_rewarded=fragments_rewarded,
            box_opened=chapter_completed,
            box_xgen=box_xgen,
            box_fragments=box_fragments,
            box_items=box_items,
        )
