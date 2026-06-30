"""add bundle_items to shop_items

Revision ID: s1t2u3v4w5x6
Revises: r1s2t3u4v5w6
Create Date: 2026-06-30 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 's1t2u3v4w5x6'
down_revision: Union[str, Sequence[str], None] = 'r1s2t3u4v5w6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('shop_items', sa.Column('bundle_items', JSONB, nullable=False, server_default='[]'))


def downgrade() -> None:
    op.drop_column('shop_items', 'bundle_items')
