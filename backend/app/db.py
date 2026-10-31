import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    write_revision: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class Record(Base):
    """Versioned user aggregates; payload contracts are validated by API schemas."""

    __tablename__ = "records"
    __table_args__ = (
        Index("uq_record_version", "user_id", "kind", "version", unique=True),
        Index("ix_record_history", "user_id", "kind", "event_date", "version"),
        Index("ix_record_parent", "user_id", "kind", "parent_ref"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict] = mapped_column(JSON)
    event_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    parent_ref: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    label: Mapped[str] = mapped_column(
        String(80), default="Local recovery session", server_default="Local recovery session"
    )


class ExternalIdentity(Base):
    __tablename__ = "external_identities"
    __table_args__ = (Index("uq_external_identity", "issuer", "subject", unique=True),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    issuer: Mapped[str] = mapped_column(String(512))
    subject: Mapped[str] = mapped_column(String(255))


class OIDCFlow(Base):
    __tablename__ = "oidc_flows"
    state_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class OperatorCounter(Base):
    __tablename__ = "operator_counters"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, server_default="0")


class RateBucket(Base):
    __tablename__ = "rate_buckets"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class FighterSnapshot(Base):
    __tablename__ = "fighter_snapshots"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    verified_at: Mapped[str] = mapped_column(String(10), index=True)
    search_name: Mapped[str] = mapped_column(String(150), default="", server_default="")
    competition_category: Mapped[str] = mapped_column(
        String(8), default="Unknown", server_default="Unknown"
    )
    career: Mapped[str] = mapped_column(String(20), default="Unknown", server_default="Unknown")
    stance_index: Mapped[str] = mapped_column(
        String(12), default="Unknown", server_default="Unknown"
    )
    division_index: Mapped[str] = mapped_column(String(500), default="", server_default="")
    current_division_index: Mapped[str] = mapped_column(String(80), default="", server_default="")
    valid_index: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    __table_args__ = (
        Index("ix_fighter_search", "valid_index", "competition_category", "search_name", "id"),
        Index(
            "uq_fighter_identity",
            "competition_category",
            "search_name",
            unique=True,
            sqlite_where=text("valid_index = 1"),
            postgresql_where=text("valid_index = true"),
        ),
    )


class ReferenceSnapshot(Base):
    __tablename__ = "reference_snapshots"
    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)


class FighterDataRevision(Base):
    __tablename__ = "fighter_data_revisions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity: Mapped[str] = mapped_column(String(80), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    archived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mma.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
    if DATABASE_URL.startswith("sqlite")
    else {"connect_timeout": 5},
    pool_pre_ping=True,
    hide_parameters=True,
)
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def sqlite_constraints(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


Session = sessionmaker(engine, expire_on_commit=False)


@event.listens_for(Session, "before_flush")
def index_fighters(db, flush_context, instances):
    from .fighter_index import metadata
    from .history_index import metadata as history_metadata

    for row in set(db.new) | set(db.dirty):
        if isinstance(row, FighterSnapshot):
            for key, value in metadata(row.payload).items():
                setattr(row, key, value)
        if isinstance(row, Record):
            for key, value in history_metadata(row).items():
                setattr(row, key, value)


class FighterImportBatch(Base):
    __tablename__ = "fighter_import_batches"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
