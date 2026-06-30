from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, func
from uuid import UUID

from app.domain.entities.guide_progress import UnlockedArticle, ChapterCompletion
from app.domain.entities.leaderboard_entry import LeaderboardEntry
from app.domain.repositories.guide_progress_repository import GuideProgressRepository, ArticleTriggerProgress
from app.infrastructure.persistence.models.player_orm import PlayerORM
from app.infrastructure.persistence.models.chapter_orm import ChapterORM
from app.infrastructure.persistence.models.guide_progress_orm import UnlockedArticleORM, ChapterCompletionORM, ArticleTriggerProgressORM


class SQLAlchemyGuideProgressRepository(GuideProgressRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_unlocked_articles_ids(self, player_id: UUID) -> set[UUID]:
        # Выбираем только ID статей, чтобы не тянуть лишние данные
        stmt = select(UnlockedArticleORM.article_id).where(UnlockedArticleORM.player_id == player_id)
        result = await self.session.execute(stmt)

        return set(result.scalars().all())

    async def save_unlocked_article(self, unlocked: UnlockedArticle) -> None:
        orm_obj = UnlockedArticleORM(
            id=unlocked.id,
            player_id=unlocked.player_id,
            article_id=unlocked.article_id,
            unlocked_at=unlocked.unlocked_at
        )
        self.session.add(orm_obj)

    async def save_chapter_completion(self, completion: ChapterCompletion) -> None:
        orm_obj = ChapterCompletionORM(
            id=completion.id,
            player_id=completion.player_id,
            chapter_id=completion.chapter_id,
            completed_at=completion.completed_at
        )
        self.session.add(orm_obj)

    async def is_chapter_completed(self, player_id: UUID, chapter_id: UUID) -> bool:
        stmt = select(ChapterCompletionORM).where(
            ChapterCompletionORM.player_id == player_id,
            ChapterCompletionORM.chapter_id == chapter_id
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_article_unlocked(self, player_id: UUID, article_id: UUID) -> bool:
        stmt = select(
            exists().where(
                UnlockedArticleORM.player_id == player_id,
                UnlockedArticleORM.article_id == article_id
            )
        )
        # scalar() сразу вернет булево значение (True/False) из базы
        return await self.session.scalar(stmt)


    async def get_trigger_progress(self, player_id: UUID, article_id: UUID) -> ArticleTriggerProgress | None:
        stmt = select(ArticleTriggerProgressORM).where(
            ArticleTriggerProgressORM.player_id == player_id,
            ArticleTriggerProgressORM.article_id == article_id
        )

        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return ArticleTriggerProgress(
            id=orm.id,
            player_id=orm.player_id,
            article_id=orm.article_id,
            current_count=orm.current_count
        )

    async def save_trigger_progress(self, progress: ArticleTriggerProgress) -> None:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = pg_insert(ArticleTriggerProgressORM).values(
            id=progress.id,
            player_id=progress.player_id,
            article_id=progress.article_id,
            current_count=progress.current_count
        ).on_conflict_do_update(
            index_elements=['id'],
            set_={'current_count': progress.current_count}
        )
        await self.session.execute(stmt)


    async def get_season_leaderboard(self, season_id: UUID, limit: int = 100) -> list[LeaderboardEntry]:
        # 1. Указываем, какие именно колонки мы хотим получить
        stmt = select(
            PlayerORM.username,
            ChapterORM.name.label("chapter_name"), # label нужен, чтобы в Row было удобное имя
            ChapterCompletionORM.completed_at
        )

        # 2. Делаем JOIN (SQLAlchemy сам поймет, как их связать, если указать условия)
        stmt = stmt.join(PlayerORM, ChapterCompletionORM.player_id == PlayerORM.id)
        stmt = stmt.join(ChapterORM, ChapterCompletionORM.chapter_id == ChapterORM.id)

        # 3. Фильтруем только сезонные главы нужного сезона
        stmt = stmt.where(ChapterORM.season_id == season_id)

        # 4. Сортируем по времени завершения (кто первый успел - тот и сверху)
        stmt = stmt.order_by(ChapterCompletionORM.completed_at.asc())

        # 5. Ограничиваем выдачу (Топ-100)
        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)

        # result.all() вернет список кортежей (Row), которые мы мапим в dataclass
        return [
            LeaderboardEntry(
                username=row.username,
                chapter_name=row.chapter_name,
                completed_at=row.completed_at
            )
            for row in result.all()
        ]

    async def get_top_players_by_unlocked_articles(self, limit: int = 100) -> list[tuple[str | None, int, UUID]]:
        stmt = (
            select(
                PlayerORM.username,
                func.count(UnlockedArticleORM.id).label("articles_count"),
                PlayerORM.id,
            )
            .join(UnlockedArticleORM, PlayerORM.id == UnlockedArticleORM.player_id)
            .group_by(PlayerORM.id, PlayerORM.username)
            .order_by(func.count(UnlockedArticleORM.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [(row.username, row.articles_count, row.id) for row in result.all()]

    async def get_player_rank_by_unlocked_articles(self, player_id: UUID) -> int:
        player_count = await self.session.execute(
            select(func.count(UnlockedArticleORM.id))
            .where(UnlockedArticleORM.player_id == player_id)
        )
        player_articles = player_count.scalar_one() or 0

        subq = (
            select(UnlockedArticleORM.player_id, func.count(UnlockedArticleORM.id).label("cnt"))
            .group_by(UnlockedArticleORM.player_id)
            .subquery()
        )
        result = await self.session.execute(
            select(func.count())
            .select_from(subq)
            .where(subq.c.cnt > player_articles)
        )
        return result.scalar_one() + 1


