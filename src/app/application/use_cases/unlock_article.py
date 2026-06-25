from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.domain.entities.player import Player
from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.guide_progress_repository import GuideProgressRepository
from app.application.dtos.guide_dto import UnlockArticleResponseDTO


class UnlockArticleUseCase:
    def __init__(self, player_repo: PlayerRepository, chapter_repo: ChapterRepository, guide_repo: GuideProgressRepository):
        self.player_repo = player_repo
        self.chapter_repo = chapter_repo
        self.guide_repo = guide_repo

    async def execute(self, player: Player, article_id: UUID) -> UnlockArticleResponseDTO:
        # 2. Достаем главу по article_id
        chapter = await self.chapter_repo.get_chapter_by_article_id(article_id)
        if not chapter:
            raise ValueError("Article or chapter not found")

        # 3. Ищем саму статью внутри главы
        article = next((a for a in chapter.articles if a.id == article_id), None)
        if not article:
            raise ValueError("Article not found in chapter")

        # 4. Проверка: нельзя купить секретные статьи
        if chapter.is_secret or article.trigger_event_type:
            raise ValueError("Cannot buy secret articles")

        # 5. Проверка: не куплена ли уже
        if await self.guide_repo.is_article_unlocked(player_id=player.id, article_id=article.id):
            raise ValueError("Already unlocked")

        # 6. Транзакция: списываем фрагменты (кинет ValueError, если не хватает)
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

        # 9. Сохраняем игрока (с обновленным балансом фрагментов и, возможно, xgen)
        await self.player_repo.save(player)

        return UnlockArticleResponseDTO(
            content=article.content,
            new_fragments_balance=player.fragments_balance,
            chapter_completed=chapter_completed,
            xgen_rewarded=xgen_rewarded,
            fragments_rewarded=fragments_rewarded
        )