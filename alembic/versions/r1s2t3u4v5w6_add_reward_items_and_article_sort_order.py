"""add reward_items to chapters and sort_order to articles

Revision ID: r1s2t3u4v5w6
Revises: q1w2e3r4t5y6
Create Date: 2026-06-30 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 'r1s2t3u4v5w6'
down_revision: Union[str, Sequence[str], None] = 'q1w2e3r4t5y6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapters', sa.Column('reward_items', JSONB, nullable=False, server_default='[]'))
    op.add_column('articles', sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('articles', 'sort_order')
    op.drop_column('chapters', 'reward_items')
