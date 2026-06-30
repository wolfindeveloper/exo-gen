from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Uuid, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.article_orm import ArticleORM

class ChapterORM(Base):
    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_secret: Mapped[bool] = mapped_column(Boolean)
    season_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("seasons.id"), nullable=True)
    reward_xgen: Mapped[int] = mapped_column(Integer, default=0)
    reward_fragments: Mapped[int] = mapped_column(Integer, default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    articles: Mapped[list["ArticleORM"]] = relationship(back_populates="chapter", cascade="all, delete-orphan")