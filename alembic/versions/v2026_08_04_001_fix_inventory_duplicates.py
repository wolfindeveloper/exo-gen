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
    # 1. Агрегируем quantities: SUM + MIN(id) для сохранения первичного ключа
    op.execute("""
        CREATE TEMP TABLE inventory_aggregated AS
        SELECT
            player_id,
            item_id,
            SUM(quantity) as total_quantity,
            MIN(id) as keep_id,
            MIN(item_metadata) as metadata
        FROM inventory_items
        GROUP BY player_id, item_id
    """)

    # 2. Очищаем основную таблицу
    op.execute("DELETE FROM inventory_items")

    # 3. Вставляем агрегированные данные обратно
    op.execute("""
        INSERT INTO inventory_items (id, player_id, item_id, quantity, metadata)
        SELECT keep_id, player_id, item_id, total_quantity, metadata
        FROM inventory_aggregated
    """)

    # 4. Удаляем временную таблицу
    op.execute("DROP TABLE inventory_aggregated")

    # 5. Добавляем unique constraint
    op.create_unique_constraint(
        "uq_inventory_player_item",
        "inventory_items",
        ["player_id", "item_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_inventory_player_item", "inventory_items")
