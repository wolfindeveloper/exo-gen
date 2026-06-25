from uuid import UUID
from datetime import datetime
from sqlalchemy import Integer, Uuid, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base

class UnlockedArticleORM(Base):
    __tablename__ = "unlocked_articles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id"))
    article_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("articles.id"))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChapterCompletionORM(Base):
    __tablename__ = "chapters_completion"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id"))
    chapter_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("chapters.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ArticleTriggerProgressORM(Base):
    __tablename__ = "articles_trigger_progress"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id"))
    article_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("articles.id"))
    current_count: Mapped[int] = mapped_column(Integer, default=0)