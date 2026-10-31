"""Searchable fighter metadata and reversible operator imports."""

import sqlalchemy as sa
from alembic import context, op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    for name, kind, default in [
        ("search_name", sa.String(150), ""),
        ("competition_category", sa.String(8), "Unknown"),
        ("career", sa.String(20), "Unknown"),
        ("stance_index", sa.String(12), "Unknown"),
        ("division_index", sa.String(500), ""),
        ("current_division_index", sa.String(80), ""),
    ]:
        op.add_column(
            "fighter_snapshots", sa.Column(name, kind, nullable=False, server_default=default)
        )
    op.add_column(
        "fighter_snapshots",
        sa.Column("valid_index", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        "ix_fighter_search",
        "fighter_snapshots",
        ["valid_index", "competition_category", "search_name", "id"],
    )
    op.create_table(
        "fighter_import_batches",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    if not context.is_offline_mode():
        from app.fighter_index import metadata

        table = sa.table(
            "fighter_snapshots",
            sa.column("id", sa.String),
            sa.column("payload", sa.JSON),
            *(
                sa.column(k, sa.Boolean if k == "valid_index" else sa.String)
                for k in [
                    "search_name",
                    "competition_category",
                    "career",
                    "stance_index",
                    "division_index",
                    "current_division_index",
                    "valid_index",
                ]
            ),
        )
        db = op.get_bind()
        for row in db.execute(sa.select(table.c.id, table.c.payload)).all():
            db.execute(table.update().where(table.c.id == row.id).values(**metadata(row.payload)))
    op.create_index(
        "uq_fighter_identity",
        "fighter_snapshots",
        ["competition_category", "search_name"],
        unique=True,
        sqlite_where=sa.text("valid_index = 1"),
        postgresql_where=sa.text("valid_index = true"),
    )


def downgrade():
    op.drop_index("uq_fighter_identity", table_name="fighter_snapshots")
    op.drop_table("fighter_import_batches")
    op.drop_index("ix_fighter_search", table_name="fighter_snapshots")
    for name in [
        "valid_index",
        "current_division_index",
        "division_index",
        "stance_index",
        "career",
        "competition_category",
        "search_name",
    ]:
        op.drop_column("fighter_snapshots", name)
