from uuid import UUID
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Date, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.ship_orm import ShipORM

class PlayerORM(Base):
    __tablename__ = "players"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, index=True, unique=True)
    username: Mapped[str | None] = mapped_column(String(30), nullable=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    xgen_balance: Mapped[int] = mapped_column(Integer, server_default="0")
    fragments_balance: Mapped[int] = mapped_column(Integer, server_default="0")
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_login_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    total_expeditions: Mapped[int] = mapped_column(Integer, default=0)
    total_artifacts_found: Mapped[int] = mapped_column(Integer, default=0)
    ships: Mapped[List["ShipORM"]] = relationship(
        back_populates="player", 
        cascade="all, delete-orphan"
    )