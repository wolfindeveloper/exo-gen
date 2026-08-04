"""Fix inventory duplicates: aggregate quantities then add unique constraint

Revision ID: v2026_08_04_001
Revises: v2026_07_31_002
Create Date: 2026-08-04 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'v2026_08_04_001'
down_revision: Union[str, Sequence[str], None] = 'v2026_07_31_002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Удаляем дубли (оставляем первую запись по id на каждую пару player_id, item_id)
    op.execute("""
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY player_id, item_id ORDER BY id
            ) as rn
            FROM inventory_items
        )
        DELETE FROM inventory_items WHERE id IN (
            SELECT id FROM ranked WHERE rn > 1
        )
    """)

    # 2. Обнов quantities до SUM (на случай если дубли уже были удалены, но quantities не сложены)
    op.execute("""
        UPDATE inventory_items i
        SET quantity = sub.total_quantity
        FROM (
            SELECT player_id, item_id, SUM(quantity) as total_quantity
            FROM inventory_items
            GROUP BY player_id, item_id
        ) sub
        WHERE i.player_id = sub.player_id AND i.item_id = sub.item_id
    """)

    # 3. Добавляем unique constraint
    op.create_unique_constraint(
        "uq_inventory_player_item",
        "inventory_items",
        ["player_id", "item_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_inventory_player_item", "inventory_items")
