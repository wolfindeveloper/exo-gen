"""make shop_items.item_id nullable for pure bundles

Revision ID: t1u2v3w4x5y6
Revises: s1t2u3v4w5x6
Create Date: 2026-06-30 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 't1u2v3w4x5y6'
down_revision: Union[str, Sequence[str], None] = 's1t2u3v4w5x6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('shop_items', 'item_id',
               existing_type=sa.Uuid(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('shop_items', 'item_id',
               existing_type=sa.Uuid(),
               nullable=False)
