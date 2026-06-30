"""Add deleted_at column to players table for soft delete

Revision ID: a3b4c5d6e7f8
Revises: q1w2e3r4t5y6
Create Date: 2026-06-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'q1w2e3r4t5y6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('players',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('players', 'deleted_at')
