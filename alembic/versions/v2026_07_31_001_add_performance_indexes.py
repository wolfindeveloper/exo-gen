"""Add performance indexes for leaderboard and query optimization

Revision ID: v2026_07_31_001
Revises: 7b5c8d9e0f1a
Create Date: 2026-07-31 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v2026_07_31_001'
down_revision: Union[str, Sequence[str], None] = '7b5c8d9e0f1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Players indexes for leaderboard
    op.create_index(
        "idx_players_xp",
        "players",
        [sa.text("xp DESC")],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_players_total_expeditions",
        "players",
        [sa.text("total_expeditions DESC")],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_players_total_artifacts",
        "players",
        [sa.text("total_artifacts_found DESC")],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_players_xgen_balance",
        "players",
        [sa.text("xgen_balance DESC")],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Expeditions - for active expeditions auto-finish
    op.create_index(
        "idx_expeditions_status_ends",
        "expeditions",
        ["status", "ends_at"],
        postgresql_where=sa.text("status = 'in_progress'"),
    )

    # Unlocked articles - for guide progress
    op.create_index(
        "idx_unlocked_articles_player",
        "unlocked_articles",
        ["player_id", "article_id"],
    )

    # Purchase history - for shop analytics
    op.create_index(
        "idx_purchase_history_shop_item_date",
        "purchase_history",
        ["shop_item_id", "purchased_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_purchase_history_shop_item_date", table_name="purchase_history")
    op.drop_index("idx_unlocked_articles_player", table_name="unlocked_articles")
    op.drop_index("idx_expeditions_status_ends", table_name="expeditions")
    op.drop_index("idx_players_xgen_balance", table_name="players")
    op.drop_index("idx_players_total_artifacts", table_name="players")
    op.drop_index("idx_players_total_expeditions", table_name="players")
    op.drop_index("idx_players_xp", table_name="players")
