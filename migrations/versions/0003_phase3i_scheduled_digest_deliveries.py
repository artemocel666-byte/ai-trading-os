"""phase3i scheduled digest delivery audit

Revision ID: 0003_phase3i_digest_audit
Revises: 0002_phase2_data_constraints
Create Date: 2026-07-15 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_phase3i_digest_audit"
down_revision: str | None = "0002_phase2_data_constraints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scheduled_digest_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.Column("project_phase", sa.String(length=120), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sender_name", sa.String(length=120), nullable=False),
        sa.Column("readiness_status", sa.String(length=20), nullable=True),
        sa.Column("item_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("ready_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("incomplete_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("blocked_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("items_summary", sa.String(length=500), nullable=True),
        sa.Column("payload_preview", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedup_key", name="uq_scheduled_digest_deliveries_dedup_key"),
        sa.CheckConstraint("item_count >= 0", name="ck_scheduled_digest_item_count_non_negative"),
        sa.CheckConstraint("ready_count >= 0", name="ck_scheduled_digest_ready_count_non_negative"),
        sa.CheckConstraint(
            "incomplete_count >= 0",
            name="ck_scheduled_digest_incomplete_count_non_negative",
        ),
        sa.CheckConstraint(
            "blocked_count >= 0",
            name="ck_scheduled_digest_blocked_count_non_negative",
        ),
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_delivered_at",
        "scheduled_digest_deliveries",
        ["delivered_at"],
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_project_phase",
        "scheduled_digest_deliveries",
        ["project_phase"],
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_readiness_status",
        "scheduled_digest_deliveries",
        ["readiness_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_scheduled_digest_deliveries_readiness_status",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_index(
        "ix_scheduled_digest_deliveries_project_phase",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_index(
        "ix_scheduled_digest_deliveries_delivered_at",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_table("scheduled_digest_deliveries")
