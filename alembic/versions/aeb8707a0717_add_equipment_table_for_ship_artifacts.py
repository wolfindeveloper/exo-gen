"""Add equipment table for ship artifacts

Revision ID: aeb8707a0717
Revises: f268ddf7b58f
Create Date: 2026-06-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aeb8707a0717'
down_revision: Union[str, Sequence[str], None] = 'f268ddf7b58f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('equipment',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('ship_id', sa.Uuid(), nullable=False),
        sa.Column('artifacts', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['ship_id'], ['ships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ship_id'),
    )


def downgrade() -> None:
    op.drop_table('equipment')
