"""phase10-4 positioning

Adds one table and drops nothing, the same shape as migration 0005.

**`open_interest` carries a positivity check and the position columns do not.** A speculative long
or short can legitimately be zero; open interest cannot, because the share this project reports is
a position divided by it. Enforcing that at the boundary means a row that would become a division
by zero is refused where the refusal is readable, rather than arriving downstream as a position of
zero.

**`contract_code` is stored beside the currency on purpose.** Both `NZ DOLLAR` and `USD INDEX` were
renamed in early 2022 while their codes stayed put, so the code is the stable identity and the
column records which series a row actually came from.

Revision ID: 0006_phase10_4_positioning
Revises: 0005_phase9d3_interest_rates
Create Date: 2026-08-22 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_phase10_4_positioning"
down_revision: str | None = "0005_phase9d3_interest_rates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "positioning_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("contract_code", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("report_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("noncommercial_long", sa.Integer(), nullable=False),
        sa.Column("noncommercial_short", sa.Integer(), nullable=False),
        sa.Column("open_interest", sa.Integer(), nullable=False),
        sa.Column("is_basket", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("currency", "report_date", name="uq_positioning_identity"),
        sa.CheckConstraint("open_interest > 0", name="ck_positioning_open_interest_positive"),
        sa.CheckConstraint("noncommercial_long >= 0", name="ck_positioning_long_not_negative"),
        sa.CheckConstraint("noncommercial_short >= 0", name="ck_positioning_short_not_negative"),
    )
    op.create_index("ix_positioning_currency", "positioning_readings", ["currency"])
    op.create_index("ix_positioning_report_date", "positioning_readings", ["report_date"])
    op.create_index(
        "ix_positioning_currency_report_date",
        "positioning_readings",
        ["currency", "report_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_positioning_currency_report_date", table_name="positioning_readings")
    op.drop_index("ix_positioning_report_date", table_name="positioning_readings")
    op.drop_index("ix_positioning_currency", table_name="positioning_readings")
    op.drop_table("positioning_readings")
