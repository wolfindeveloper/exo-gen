"""add bundle metadata fields to shop_items

Revision ID: v2026_08_04_002
Revises: v2026_08_04_001
Create Date: 2026-08-04 13:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "v2026_08_04_002"
down_revision: Union[str, None] = "v2026_08_04_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("shop_items", sa.Column("bundle_name", sa.String(200), server_default="", nullable=False))
    op.add_column("shop_items", sa.Column("bundle_description", sa.Text(), server_default="", nullable=False))
    op.add_column("shop_items", sa.Column("bundle_image_url", sa.String(500), server_default="", nullable=False))


def downgrade() -> None:
    op.drop_column("shop_items", "bundle_image_url")
    op.drop_column("shop_items", "bundle_description")
    op.drop_column("shop_items", "bundle_name")
