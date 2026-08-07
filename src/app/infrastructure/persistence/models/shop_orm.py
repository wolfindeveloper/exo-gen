from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text, Uuid, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.item_orm import ItemORM


class ShopCategoryORM(Base):
    __tablename__ = "shop_categories"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    icon: Mapped[str] = mapped_column(String(10), default="", server_default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ShopItemORM(Base):
    __tablename__ = "shop_items"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    item_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("items.id", ondelete="CASCADE"), nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("shop_categories.id"), nullable=True, index=True)
    price_xgen: Mapped[int] = mapped_column(Integer, default=0)
    daily_limit: Mapped[int] = mapped_column(Integer, default=0)
    stock_limit: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bundle_items: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    bundle_name: Mapped[str] = mapped_column(String(200), default="", server_default="")
    bundle_description: Mapped[str] = mapped_column(Text, default="", server_default="")
    bundle_image_url: Mapped[str] = mapped_column(String(500), default="", server_default="")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    item: Mapped["ItemORM"] = relationship()


class PurchaseHistoryORM(Base):
    __tablename__ = "purchase_history"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    player_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("players.id", ondelete="RESTRICT"), nullable=False, index=True)
    shop_item_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("shop_items.id"), nullable=False, index=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
