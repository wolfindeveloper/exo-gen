"""Remove slot_type from equipment artifacts JSONB

Revision ID: v2026_07_31_002
Revises: v2026_07_31_001
Create Date: 2026-07-31 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v2026_07_31_002'
down_revision: Union[str, Sequence[str], None] = 'v2026_07_31_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, artifacts FROM equipment")).fetchall()

    for row in rows:
        equipment_id = row[0]
        artifacts = row[1] or []
        updated = []
        for a in artifacts:
            updated.append({
                "item_id": a["item_id"],
                "bonuses": a.get("bonuses", {}),
            })
        conn.execute(
            sa.text("UPDATE equipment SET artifacts = :artifacts WHERE id = :id"),
            {"artifacts": sa.types.JSON().bind_processor(sa.dialects.postgresql.JSONB)(updated), "id": equipment_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, artifacts FROM equipment")).fetchall()

    for row in rows:
        equipment_id = row[0]
        artifacts = row[1] or []
        updated = []
        for a in artifacts:
            updated.append({
                "item_id": a["item_id"],
                "slot_type": "speed",
                "bonuses": a.get("bonuses", {}),
            })
        conn.execute(
            sa.text("UPDATE equipment SET artifacts = :artifacts WHERE id = :id"),
            {"artifacts": sa.types.JSON().bind_processor(sa.dialects.postgresql.JSONB)(updated), "id": equipment_id},
        )
