"""add tier column to zones

Revision ID: u1v2w3x4y5z6
Revises: t1u2v3w4x5y6
Create Date: 2026-07-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'u1v2w3x4y5z6'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'


def upgrade() -> None:
    op.add_column('zones', sa.Column('tier', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('zones', 'tier')
