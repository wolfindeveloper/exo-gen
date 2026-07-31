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
    # CONCURRENTLY indexes cannot run inside a transaction
    # We need to use individual execution with autocommit
    connection = op.get_bind()
    
    # 1. Players table - leaderboard indexes
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_players_xp ON players(xp DESC) WHERE deleted_at IS NULL"
    ))
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_players_total_expeditions ON players(total_expeditions DESC) WHERE deleted_at IS NULL"
    ))
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_players_total_artifacts ON players(total_artifacts_found DESC) WHERE deleted_at IS NULL"
    ))
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_players_xgen_balance ON players(xgen_balance DESC) WHERE deleted_at IS NULL"
    ))
    
    # 2. Expeditions table - status and ends_at for auto-finish
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_expeditions_status_ends ON expeditions(status, ends_at) WHERE status = 'in_progress'"
    ))
    
    # 3. Unlocked articles - player_id and article_id for guide progress
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_unlocked_articles_player ON unlocked_articles(player_id, article_id)"
    ))
    
    # 4. Purchase history - shop_item_id and purchased_at for daily/total limits
    connection.execute(sa.text(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_purchase_history_shop_item_date ON purchase_history(shop_item_id, purchased_at)"
    ))


def downgrade() -> None:
    connection = op.get_bind()
    
    # Drop indexes in reverse order
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_purchase_history_shop_item_date"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_unlocked_articles_player"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_expeditions_status_ends"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_players_xgen_balance"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_players_total_artifacts"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_players_total_expeditions"))
    connection.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS idx_players_xp"))
