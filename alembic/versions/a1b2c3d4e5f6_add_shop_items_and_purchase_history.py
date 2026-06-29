"""Add shop_items and purchase_history tables

Revision ID: a1b2c3d4e5f6
Revises: eef3ca74103a
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'eef3ca74103a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('shop_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('item_id', sa.Uuid(), nullable=False),
        sa.Column('price_xgen', sa.Integer(), nullable=False),
        sa.Column('daily_limit', sa.Integer(), nullable=False),
        sa.Column('stock_limit', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_shop_items_id'), 'shop_items', ['id'], unique=False)

    op.create_table('purchase_history',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('player_id', sa.Uuid(), nullable=False),
        sa.Column('shop_item_id', sa.Uuid(), nullable=False),
        sa.Column('purchased_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shop_item_id'], ['shop_items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_purchase_history_id'), 'purchase_history', ['id'], unique=False)
    op.create_index('ix_purchase_history_player_shop_item', 'purchase_history', ['player_id', 'shop_item_id'], unique=False)


def downgrade() -> None:
    op.drop_table('purchase_history')
    op.drop_table('shop_items')
