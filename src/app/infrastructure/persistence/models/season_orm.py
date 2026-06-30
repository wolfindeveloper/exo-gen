from uuid import UUID
from datetime import datetime
from sqlalchemy import Integer, String, Uuid, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base

class SeasonORM(Base):
    __tablename__ = "seasons"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reward_xgen: Mapped[int] = mapped_column(Integer, default=0)
    reward_fragments: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)