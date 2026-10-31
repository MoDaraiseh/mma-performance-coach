"""Serialize versioned account writes and approvals.

Revision ID: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("write_revision", sa.Integer(), nullable=False, server_default="0")
    )


def downgrade():
    op.drop_column("users", "write_revision")
