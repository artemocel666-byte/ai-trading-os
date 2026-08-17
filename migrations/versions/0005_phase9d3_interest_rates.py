"""phase9d3 interest rates

Adds one table and drops nothing, the same shape as migration 0004.

**No positivity constraint on the rate, unlike every price column in this schema.** JPY, CHF and EUR
all spent years below zero, and a check here would reject real observations at the boundary where
the failure is hardest to read.

Revision ID: 0005_phase9d3_interest_rates
Revises: 0004_phase9c1_forward_outcomes
Create Date: 2026-08-15 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_phase9d3_interest_rates"
down_revision: str | None = "0004_phase9c1_forward_outcomes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interest_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("source_series", sa.String(length=120), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("annual_rate", sa.Numeric(12, 8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("currency", "as_of", name="uq_interest_rate_identity"),
    )
    op.create_index("ix_interest_rates_currency", "interest_rates", ["currency"])
    op.create_index("ix_interest_rates_as_of", "interest_rates", ["as_of"])
    op.create_index("ix_interest_rates_currency_as_of", "interest_rates", ["currency", "as_of"])


def downgrade() -> None:
    op.drop_index("ix_interest_rates_currency_as_of", table_name="interest_rates")
    op.drop_index("ix_interest_rates_as_of", table_name="interest_rates")
    op.drop_index("ix_interest_rates_currency", table_name="interest_rates")
    op.drop_table("interest_rates")
