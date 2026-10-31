"""Persist public reference snapshots and guard aggregate versions.

Revision ID: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("uq_record_version", "records", ["user_id", "kind", "version"], unique=True)
    op.create_table(
        "fighter_snapshots",
        sa.Column("id", sa.String(60), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("verified_at", sa.String(10), nullable=False),
    )
    op.create_index("ix_fighter_snapshots_verified_at", "fighter_snapshots", ["verified_at"])
    op.create_table(
        "reference_snapshots",
        sa.Column("id", sa.String(60), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )


def downgrade():
    op.drop_table("reference_snapshots")
    op.drop_table("fighter_snapshots")
    op.drop_index("uq_record_version", "records")
