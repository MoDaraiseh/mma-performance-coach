"""Preserve comparison-data history during explicit provider refresh."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fighter_data_revisions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("entity", sa.String(80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fighter_data_revisions_entity", "fighter_data_revisions", ["entity"])


def downgrade():
    op.drop_index("ix_fighter_data_revisions_entity", table_name="fighter_data_revisions")
    op.drop_table("fighter_data_revisions")
