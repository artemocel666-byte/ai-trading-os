"""phase2 data constraints

Revision ID: 0002_phase2_data_constraints
Revises: 0001_foundation_schema
Create Date: 2026-07-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_phase2_data_constraints"
down_revision: str | None = "0001_foundation_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("economic_events", sa.Column("country", sa.String(length=120), nullable=True))
    op.add_column("economic_events", sa.Column("actual_raw", sa.String(length=200), nullable=True))
    op.add_column(
        "economic_events", sa.Column("forecast_raw", sa.String(length=200), nullable=True)
    )
    op.add_column(
        "economic_events", sa.Column("previous_raw", sa.String(length=200), nullable=True)
    )
    op.create_unique_constraint(
        "uq_economic_events_provider_event",
        "economic_events",
        ["provider", "provider_event_id"],
    )
    op.create_check_constraint("ck_candles_open_positive", "candles", "open > 0")
    op.create_check_constraint("ck_candles_high_positive", "candles", "high > 0")
    op.create_check_constraint("ck_candles_low_positive", "candles", "low > 0")
    op.create_check_constraint("ck_candles_close_positive", "candles", "close > 0")
    op.create_check_constraint("ck_candles_close_after_open", "candles", "close_time > open_time")
    op.create_check_constraint(
        "ck_candles_volume_non_negative",
        "candles",
        "volume IS NULL OR volume >= 0",
    )
    op.create_check_constraint("ck_candles_is_closed", "candles", "is_closed = true")


def downgrade() -> None:
    op.drop_constraint("ck_candles_is_closed", "candles", type_="check")
    op.drop_constraint("ck_candles_volume_non_negative", "candles", type_="check")
    op.drop_constraint("ck_candles_close_after_open", "candles", type_="check")
    op.drop_constraint("ck_candles_close_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_low_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_high_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_open_positive", "candles", type_="check")
    op.drop_constraint("uq_economic_events_provider_event", "economic_events", type_="unique")
    op.drop_column("economic_events", "previous_raw")
    op.drop_column("economic_events", "forecast_raw")
    op.drop_column("economic_events", "actual_raw")
    op.drop_column("economic_events", "country")
