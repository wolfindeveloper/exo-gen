"""Add deleted_at column to reference tables for soft delete

Revision ID: b1c2d3e4f5g6
Revises: a3b4c5d6e7f8
Create Date: 2026-06-30 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = [
    'items',
    'zones',
    'chapters',
    'articles',
    'seasons',
    'loot_box_configs',
    'shop_items',
    'stars_packages',
]


def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(
            table_name,
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    for table_name in TABLES:
        op.drop_column(table_name, 'deleted_at')
