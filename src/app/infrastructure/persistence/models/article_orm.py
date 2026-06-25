from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Uuid, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.chapter_orm import ChapterORM

class ArticleORM(Base):
    __tablename__ = "articles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    chapter_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("chapters.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    fragment_cost: Mapped[int] = mapped_column(Integer, default=0)
    trigger_event_type: Mapped[str | None] = mapped_column(String, nullable=True)
    trigger_threshold: Mapped[int] = mapped_column(Integer, default=1)
    # Связь с предметом-ключом
    required_item_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("items.id"), nullable=True)

    chapter: Mapped["ChapterORM"] = relationship(back_populates="articles")