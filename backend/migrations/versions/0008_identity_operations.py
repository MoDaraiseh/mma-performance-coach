"""Managed identity bindings, single-use OIDC flows and operational counters."""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    # Add nullable, backfill, then constrain: compatible with existing SQLite and PostgreSQL.
    op.add_column(
        "login_sessions", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.execute(
        sa.text("UPDATE login_sessions SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL")
    )
    with op.batch_alter_table("login_sessions") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.add_column(
            sa.Column(
                "label", sa.String(80), nullable=False, server_default="Local recovery session"
            )
        )
    op.create_table(
        "external_identities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("issuer", sa.String(512), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
    )
    op.create_index("ix_external_identities_user_id", "external_identities", ["user_id"])
    op.create_index(
        "uq_external_identity", "external_identities", ["issuer", "subject"], unique=True
    )
    op.create_table(
        "oidc_flows",
        sa.Column("state_hash", sa.String(64), primary_key=True),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_oidc_flows_expires_at", "oidc_flows", ["expires_at"])
    op.create_table(
        "operator_counters",
        sa.Column("key", sa.String(80), primary_key=True),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_table("operator_counters")
    op.drop_table("oidc_flows")
    op.drop_table("external_identities")
    with op.batch_alter_table("login_sessions") as batch:
        batch.drop_column("label")
        batch.drop_column("created_at")
