"""change telegram_id from INTEGER to BIGINT

Revision ID: 7b5c8d9e0f1a
Revises: u1v2w3x4y5z6
Create Date: 2026-07-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7b5c8d9e0f1a'
down_revision: Union[str, Sequence[str], None] = 'u1v2w3x4y5z6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'players',
        'telegram_id',
        type_=sa.BigInteger(),
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.drop_index('ix_players_telegram_id', table_name='players')
    op.create_index('ix_players_telegram_id', 'players', ['telegram_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_players_telegram_id', table_name='players')
    op.alter_column(
        'players',
        'telegram_id',
        type_=sa.Integer(),
        existing_type=sa.BigInteger(),
        existing_nullable=False,
    )
    op.create_index('ix_players_telegram_id', 'players', ['telegram_id'], unique=True)
