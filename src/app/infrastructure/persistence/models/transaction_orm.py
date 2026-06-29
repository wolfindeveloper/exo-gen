from uuid import UUID
from datetime import datetime

from sqlalchemy import Integer, String, Uuid, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id"), nullable=False, index=True)
    telegram_charge_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    stars_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    xgen_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
