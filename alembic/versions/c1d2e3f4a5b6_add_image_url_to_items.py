"""Add image_url column to items table

Revision ID: c1d2e3f4a5b6
Revises: 29deb3eb8ab6
Create Date: 2026-07-01 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = '29deb3eb8ab6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'items',
        sa.Column('image_url', sa.String(500), nullable=False, server_default=''),
    )


def downgrade() -> None:
    op.drop_column('items', 'image_url')
