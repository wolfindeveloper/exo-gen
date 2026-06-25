from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.domain.entities.player import Player
from app.domain.uow import UnitOfWork
from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion
from app.domain.exceptions.guide import ArticleNotFoundError, ChapterNotFoundError, ArticleAlreadyUnlockedError, CannotBuySecretArticleError
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import UnlockArticleResponseDTO


class UnlockArticleUseCase:
    def __init__(self, player_repo: PlayerRepository, chapter_repo: ChapterRepository, guide_repo: GuideProgressRepository):
        self.player_repo = player_repo
        self.chapter_repo = chapter_repo
        self.guide_repo = guide_repo

    async def execute(self, player: Player, article_id: UUID, uow: UnitOfWork) -> UnlockArticleResponseDTO:
        chapter = await self.chapter_repo.get_chapter_by_article_id(article_id)
        if not chapter:
            raise ChapterNotFoundError(f"Chapter for article {article_id} not found")

        article = next((a for a in chapter.articles if a.id == article_id), None)
        if not article:
            raise ArticleNotFoundError(f"Article {article_id} not found in chapter")

        if chapter.is_secret or article.trigger_event_type:
            raise CannotBuySecretArticleError("Cannot buy secret articles")

        if await self.guide_repo.is_article_unlocked(player_id=player.id, article_id=article.id):
            raise ArticleAlreadyUnlockedError(f"Article {article_id} already unlocked")

        player.spend_fragments(article.fragment_cost)

        # 7. Создаем запись об открытии и сохраняем
        unlocked = UnlockedArticle(
            id=uuid4(),
            player_id=player.id,
            article_id=article.id,
            unlocked_at=datetime.now(timezone.utc)
        )
        await self.guide_repo.save_unlocked_article(unlocked)

        # 8. Проверяем, завершена ли глава целиком
        chapter_completed = False
        xgen_rewarded = 0
        fragments_rewarded = 0

        # Считаем только ОБЫЧНЫЕ статьи (не секретные)
        regular_articles = [a for a in chapter.articles if not a.trigger_event_type]
        total_regular = len(regular_articles)

        if total_regular > 0:
            # Получаем все открытые ID у игрока
            unlocked_ids = await self.guide_repo.get_unlocked_articles_ids(player.id)

            # Считаем, сколько обычных статей этой главы открыто
            regular_article_ids = {a.id for a in regular_articles}
            unlocked_regular_count = len(regular_article_ids.intersection(unlocked_ids))

            # Если открыты все обычные статьи И глава еще не была завершена
            if unlocked_regular_count == total_regular:
                is_completed = await self.guide_repo.is_chapter_completed(player.id, chapter.id)
                if not is_completed:
                    # Начисляем награду
                    player.add_xgen(chapter.reward_xgen)
                    player.add_fragments(chapter.reward_fragments)

                    xgen_rewarded = chapter.reward_xgen
                    fragments_rewarded = chapter.reward_fragments

                    # Создаем запись о завершении
                    completion = ChapterCompletion(
                        id=uuid4(),
                        player_id=player.id,
                        chapter_id=chapter.id,
                        completed_at=datetime.now(timezone.utc)
                    )
                    await self.guide_repo.save_chapter_completion(completion)
                    chapter_completed = True

        await self.player_repo.save(player)
        await uow.commit()

        return UnlockArticleResponseDTO(
            content=article.content,
            new_fragments_balance=player.fragments_balance,
            chapter_completed=chapter_completed,
            xgen_rewarded=xgen_rewarded,
            fragments_rewarded=fragments_rewarded
        )