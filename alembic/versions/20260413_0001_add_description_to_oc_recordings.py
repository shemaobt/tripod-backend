"""add description column to oc_recordings

Revision ID: 20260413_0001
Revises: 20260401_0001
Create Date: 2026-04-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260413_0001"
down_revision: str | None = "20260401_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "oc_recordings",
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("oc_recordings", "description")
