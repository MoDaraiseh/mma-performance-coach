"""Indexed event dates and plan lineage references; payloads are untouched."""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("records", sa.Column("event_date", sa.String(10), nullable=True))
    op.add_column("records", sa.Column("parent_ref", sa.String(36), nullable=True))
    table = sa.table(
        "records",
        sa.column("id", sa.String),
        sa.column("kind", sa.String),
        sa.column("payload", sa.JSON),
        sa.column("created_at", sa.DateTime),
        sa.column("event_date", sa.String),
        sa.column("parent_ref", sa.String),
    )
    op.execute(
        table.update()
        .where(table.c.kind.in_(["checkin", "technical_achievement"]))
        .values(event_date=table.c.payload["date"].as_string())
    )
    op.execute(
        table.update()
        .where(table.c.kind == "workout")
        .values(
            event_date=sa.func.coalesce(
                table.c.payload["completed_on"].as_string(),
                sa.func.substr(sa.cast(table.c.created_at, sa.String), 1, 10),
            ),
            parent_ref=table.c.payload["plan_id"].as_string(),
        )
    )
    op.execute(
        table.update()
        .where(table.c.kind == "plan")
        .values(parent_ref=sa.func.coalesce(table.c.payload["lineage_id"].as_string(), table.c.id))
    )
    op.create_index("ix_record_history", "records", ["user_id", "kind", "event_date", "version"])
    op.create_index("ix_record_parent", "records", ["user_id", "kind", "parent_ref"])


def downgrade():
    op.drop_index("ix_record_parent", table_name="records")
    op.drop_index("ix_record_history", table_name="records")
    op.drop_column("records", "parent_ref")
    op.drop_column("records", "event_date")
