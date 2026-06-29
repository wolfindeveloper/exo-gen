"""Add stars_packages and transactions tables

Revision ID: n1o2p3q4r5s6
Revises: a1b2c3d4e5f6
Create Date: 2026-06-29 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'n1o2p3q4r5s6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('stars_packages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('stars_amount', sa.Integer(), nullable=False),
        sa.Column('xgen_reward', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stars_packages_id'), 'stars_packages', ['id'], unique=False)

    op.create_table('transactions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('player_id', sa.Uuid(), nullable=False),
        sa.Column('telegram_charge_id', sa.Text(), nullable=False),
        sa.Column('stars_amount', sa.Integer(), nullable=False),
        sa.Column('xgen_amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_charge_id'),
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_player_id'), 'transactions', ['player_id'], unique=False)
    op.create_index(op.f('ix_transactions_telegram_charge_id'), 'transactions', ['telegram_charge_id'], unique=True)


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('stars_packages')
