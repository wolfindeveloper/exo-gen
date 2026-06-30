"""merge heads

Revision ID: 29deb3eb8ab6
Revises: b1c2d3e4f5g6, t1u2v3w4x5y6
Create Date: 2026-06-30 22:14:28.654584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29deb3eb8ab6'
down_revision: Union[str, Sequence[str], None] = ('b1c2d3e4f5g6', 't1u2v3w4x5y6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
