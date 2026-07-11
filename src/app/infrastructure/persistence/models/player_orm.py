from datetime import datetime
from uuid import UUID
from typing import List, TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Date, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.ship_orm import ShipORM
    from app.infrastructure.persistence.models.transaction_orm import TransactionORM

class PlayerORM(Base):
    __tablename__ = "players"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    username: Mapped[str | None] = mapped_column(String(30), nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    xgen_balance: Mapped[int] = mapped_column(Integer, server_default="0")
    fragments_balance: Mapped[int] = mapped_column(Integer, server_default="0")
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_login_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    total_expeditions: Mapped[int] = mapped_column(Integer, default=0)
    total_artifacts_found: Mapped[int] = mapped_column(Integer, default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ships: Mapped[List["ShipORM"]] = relationship(
        back_populates="player", 
        cascade="all, delete-orphan"
    )
    transactions: Mapped[list["TransactionORM"]] = relationship(back_populates="player")