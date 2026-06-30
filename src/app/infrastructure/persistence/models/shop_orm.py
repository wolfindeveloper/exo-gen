from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Uuid, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.item_orm import ItemORM


class ShopItemORM(Base):
    __tablename__ = "shop_items"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    item_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("items.id"), nullable=False)
    price_xgen: Mapped[int] = mapped_column(Integer, default=0)
    daily_limit: Mapped[int] = mapped_column(Integer, default=0)
    stock_limit: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bundle_items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    item: Mapped["ItemORM"] = relationship()


class PurchaseHistoryORM(Base):
    __tablename__ = "purchase_history"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id", ondelete="RESTRICT"), nullable=False, index=True)
    shop_item_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("shop_items.id"), nullable=False, index=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
