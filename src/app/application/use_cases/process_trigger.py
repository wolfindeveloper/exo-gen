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
        # 2. Достаем ВСЕ главы со статьями
        # (В идеале тут был бы метод репозитория get_articles_by_trigger(), 
        # но для MVP и малого количества глав мы фильтруем в памяти Python)
        chapters = await self.chapter_repo.get_all_with_articles()

        newly_unlocked_titles = []
        player_state_changed = False # Флаг: менялись ли балансы игрока (награды)

        # 3. Ищем все статьи, которые реагируют на это событие
        for chapter in chapters:
            # Нам нужны только статьи с подходящим триггером
            triggered_articles = [
                art for art in chapter.articles 
                if art.trigger_event_type == dto.event_type
            ]

            logger.info(f"Событие: '{dto.event_type}'. Найдено подходящих статей: {len(triggered_articles)}")
            
            if not triggered_articles:
                continue

            for article in triggered_articles:
                # 3.1. Пропускаем, если статья уже открыта
                is_unlocked = await self.guide_repo.is_article_unlocked(player.id, article.id)
                logger.debug(f"Статья: '{article.title}'. Уже открыта? {is_unlocked}")
                
                if is_unlocked:
                    continue

                # 3.2. Достаем или создаем прогресс триггера
                progress = await self.guide_repo.get_trigger_progress(player.id, article.id)
                if not progress:
                    progress = ArticleTriggerProgress(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        current_count=0
                    )

                # 3.3. Инкрементируем счетчик
                progress.current_count += 1
                logger.debug(f"Прогресс: {progress.current_count} / {article.trigger_threshold}")

                # 3.4. Проверяем, достигнут ли порог
                if progress.current_count >= article.trigger_threshold:
                    logger.info(f"Порог достигнут! Открываем статью: {article.title}")
                    # 🎉 Открываем статью!
                    unlocked = UnlockedArticle(
                        id=uuid4(),
                        player_id=player.id,
                        article_id=article.id,
                        unlocked_at=datetime.now(timezone.utc)
                    )
                    await self.guide_repo.save_unlocked_article(unlocked)
                    newly_unlocked_titles.append(article.title)

                    # --- ПРОВЕРКА ЗАВЕРШЕНИЯ СЕКРЕТНОЙ ГЛАВЫ ---
                    # Считаем все секретные статьи в этой главе (у которых есть триггер)
                    all_secret_articles = [a for a in chapter.articles if a.trigger_event_type]
                    total_secret = len(all_secret_articles)

                    if total_secret > 0:
                        # Достаем все открытые ID у игрока (включая только что открытую)
                        unlocked_ids = await self.guide_repo.get_unlocked_articles_ids(player.id)
                        secret_article_ids = {a.id for a in all_secret_articles}
                        
                        # Считаем пересечение (сколько секретных статей этой главы открыто)
                        unlocked_secret_count = len(secret_article_ids.intersection(unlocked_ids))

                        # Если открыты ВСЕ секретные статьи И глава еще не была завершена
                        if unlocked_secret_count == total_secret:
                            is_completed = await self.guide_repo.is_chapter_completed(player.id, chapter.id)
                            if not is_completed:
                                # 💰 Начисляем награду за главу
                                player.add_xgen(chapter.reward_xgen)
                                player.add_fragments(chapter.reward_fragments)
                                player_state_changed = True
                                
                                # 🏆 Фиксируем завершение (для лидерборда)
                                completion = ChapterCompletion(
                                    id=uuid4(),
                                    player_id=player.id,
                                    chapter_id=chapter.id,
                                    completed_at=datetime.now(timezone.utc)
                                )
                                await self.guide_repo.save_chapter_completion(completion)

                # Сохраняем прогресс триггера (обновленный счетчик или новую запись)
                await self.guide_repo.save_trigger_progress(progress)

        if player_state_changed:
            await self.player_repo.save(player)

        await uow.commit()

        return TriggerEventResponseDTO(newly_unlocked_articles=newly_unlocked_titles)