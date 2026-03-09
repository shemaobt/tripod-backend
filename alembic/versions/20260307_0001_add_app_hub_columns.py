"""add app hub columns to apps table

Revision ID: 20260307_0001
Revises: 20260306_0003
Create Date: 2026-03-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260307_0001"
down_revision: str | None = "20260306_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("apps", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("apps", sa.Column("icon_url", sa.String(500), nullable=True))
    op.add_column("apps", sa.Column("app_url", sa.String(500), nullable=True))
    op.add_column("apps", sa.Column("ios_url", sa.String(500), nullable=True))
    op.add_column("apps", sa.Column("android_url", sa.String(500), nullable=True))
    op.add_column(
        "apps",
        sa.Column("platform", sa.String(20), server_default="web", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("apps", "platform")
    op.drop_column("apps", "android_url")
    op.drop_column("apps", "ios_url")
    op.drop_column("apps", "app_url")
    op.drop_column("apps", "icon_url")
    op.drop_column("apps", "description")
