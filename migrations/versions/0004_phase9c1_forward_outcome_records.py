"""phase9c1 forward outcome ledger

Adds one table and drops nothing. The unused `signals` and `paper_positions` tables from
`0001_foundation_schema` are deliberately left in place: removing them is destructive, out of scope
for this slice, and they are harmless while empty.

Revision ID: 0004_phase9c1_forward_outcomes
Revises: 0003_phase3i_digest_audit
Create Date: 2026-08-10 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_phase9c1_forward_outcomes"
down_revision: str | None = "0003_phase3i_digest_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "forward_outcome_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("timeframe", sa.String(length=20), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("anchor_price", sa.Numeric(20, 10), nullable=False),
        sa.Column("entry_min", sa.Numeric(20, 10), nullable=False),
        sa.Column("entry_max", sa.Numeric(20, 10), nullable=False),
        sa.Column("stop_loss", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_1", sa.Numeric(20, 10), nullable=False),
        sa.Column("decision_status", sa.String(length=30), nullable=False),
        sa.Column("market_open", sa.Boolean(), nullable=True),
        sa.Column("failed_rule_ids_json", postgresql.JSONB(), nullable=False),
        sa.Column("pipeline_version", sa.String(length=120), nullable=False),
        sa.Column("ruleset_versions_json", postgresql.JSONB(), nullable=False),
        sa.Column("decision_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("entry_band_multiplier", sa.Numeric(10, 4), nullable=False),
        sa.Column("stop_multiplier", sa.Numeric(10, 4), nullable=False),
        sa.Column("target_multiplier", sa.Numeric(10, 4), nullable=False),
        sa.Column("horizon_candles", sa.Integer(), nullable=False),
        sa.Column("project_phase", sa.String(length=120), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome_kind", sa.String(length=20), nullable=True),
        sa.Column("bars_to_resolution", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "pair",
            "timeframe",
            "as_of",
            "direction",
            name="uq_forward_outcome_identity",
        ),
        sa.CheckConstraint("anchor_price > 0", name="ck_forward_outcome_anchor_positive"),
        sa.CheckConstraint("entry_min > 0", name="ck_forward_outcome_entry_min_positive"),
        sa.CheckConstraint("entry_max >= entry_min", name="ck_forward_outcome_entry_band_ordered"),
        sa.CheckConstraint("stop_loss > 0", name="ck_forward_outcome_stop_positive"),
        sa.CheckConstraint("take_profit_1 > 0", name="ck_forward_outcome_target_positive"),
        sa.CheckConstraint("horizon_candles >= 1", name="ck_forward_outcome_horizon_positive"),
        sa.CheckConstraint(
            "bars_to_resolution IS NULL OR bars_to_resolution >= 1",
            name="ck_forward_outcome_bars_positive",
        ),
        sa.CheckConstraint(
            "(outcome_kind IS NULL AND resolved_at IS NULL)"
            " OR (outcome_kind IS NOT NULL AND resolved_at IS NOT NULL)",
            name="ck_forward_outcome_settled_together",
        ),
        sa.CheckConstraint(
            "outcome_kind IS NOT NULL OR bars_to_resolution IS NULL",
            name="ck_forward_outcome_pending_has_no_bars",
        ),
    )
    op.create_index("ix_forward_outcome_records_pair", "forward_outcome_records", ["pair"])
    op.create_index(
        "ix_forward_outcome_records_timeframe", "forward_outcome_records", ["timeframe"]
    )
    op.create_index("ix_forward_outcome_records_as_of", "forward_outcome_records", ["as_of"])
    op.create_index(
        "ix_forward_outcome_records_decision_status",
        "forward_outcome_records",
        ["decision_status"],
    )
    op.create_index(
        "ix_forward_outcome_records_pending",
        "forward_outcome_records",
        ["outcome_kind", "as_of"],
    )
    op.create_index(
        "ix_forward_outcome_records_pair_timeframe_as_of",
        "forward_outcome_records",
        ["pair", "timeframe", "as_of"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_forward_outcome_records_pair_timeframe_as_of", table_name="forward_outcome_records"
    )
    op.drop_index("ix_forward_outcome_records_pending", table_name="forward_outcome_records")
    op.drop_index(
        "ix_forward_outcome_records_decision_status", table_name="forward_outcome_records"
    )
    op.drop_index("ix_forward_outcome_records_as_of", table_name="forward_outcome_records")
    op.drop_index("ix_forward_outcome_records_timeframe", table_name="forward_outcome_records")
    op.drop_index("ix_forward_outcome_records_pair", table_name="forward_outcome_records")
    op.drop_table("forward_outcome_records")
