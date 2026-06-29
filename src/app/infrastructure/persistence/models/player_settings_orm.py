from uuid import UUID

from sqlalchemy import Uuid, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class PlayerSettingsORM(Base):
    __tablename__ = "player_settings"

    player_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("players.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    music_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
