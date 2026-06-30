"""Fix financial FK constraints: CASCADE → RESTRICT

Revision ID: q1w2e3r4t5y6
Revises: p1q2r3s4t5u6
Create Date: 2026-06-30 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'q1w2e3r4t5y6'
down_revision: Union[str, Sequence[str], None] = 'p1q2r3s4t5u6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('transactions_player_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(
        'transactions_player_id_fkey',
        'transactions', 'players',
        ['player_id'], ['id'],
        ondelete='RESTRICT',
    )

    op.drop_constraint('purchase_history_player_id_fkey', 'purchase_history', type_='foreignkey')
    op.create_foreign_key(
        'purchase_history_player_id_fkey',
        'purchase_history', 'players',
        ['player_id'], ['id'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    op.drop_constraint('purchase_history_player_id_fkey', 'purchase_history', type_='foreignkey')
    op.create_foreign_key(
        'purchase_history_player_id_fkey',
        'purchase_history', 'players',
        ['player_id'], ['id'],
        ondelete='CASCADE',
    )

    op.drop_constraint('transactions_player_id_fkey', 'transactions', type_='foreignkey')
    op.create_foreign_key(
        'transactions_player_id_fkey',
        'transactions', 'players',
        ['player_id'], ['id'],
        ondelete='CASCADE',
    )
