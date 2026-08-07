"""add shop_categories table and category_id to shop_items

Revision ID: v2026_08_07_001
Revises: v2026_08_04_003
Create Date: 2026-08-07 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "v2026_08_07_001"
down_revision: Union[str, None] = "v2026_08_04_003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "shop_categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("icon", sa.String(10), server_default="", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.add_column(
        "shop_items",
        sa.Column("category_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_shop_items_category_id_shop_categories",
        "shop_items",
        "shop_categories",
        ["category_id"],
        ["id"],
    )
    op.create_index(
        "ix_shop_items_category_id",
        "shop_items",
        ["category_id"],
    )

    op.execute(
        """
        INSERT INTO shop_categories (id, name, slug, icon, sort_order, is_active)
        VALUES
            (gen_random_uuid(), 'Ресурсы', 'resources', '📦', 1, true),
            (gen_random_uuid(), 'Артефакты', 'artifacts', '✨', 2, true),
            (gen_random_uuid(), 'Наборы', 'bundles', '🎁', 3, true),
            (gen_random_uuid(), 'Премиум', 'premium', '⭐', 4, true)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_shop_items_category_id", table_name="shop_items")
    op.drop_constraint(
        "fk_shop_items_category_id_shop_categories",
        "shop_items",
        type_="foreignkey",
    )
    op.drop_column("shop_items", "category_id")
    op.drop_table("shop_categories")
