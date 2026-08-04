"""add notified_at to expeditions for push notification tracking

Revision ID: v2026_08_04_003
Revises: v2026_08_04_002
Create Date: 2026-08-04 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "v2026_08_04_003"
down_revision: Union[str, None] = "v2026_08_04_002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expeditions",
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_expeditions_finished_notified",
        "expeditions",
        ["status", "notified_at"],
        postgresql_where=sa.text("status = 'finished'"),
    )


def downgrade() -> None:
    op.drop_index("idx_expeditions_finished_notified", table_name="expeditions")
    op.drop_column("expeditions", "notified_at")
