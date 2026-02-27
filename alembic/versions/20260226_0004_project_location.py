"""project location (latitude, longitude, location_display_name)

Revision ID: 20260226_0004
Revises: 20260226_0003
Create Date: 2026-02-26 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "20260226_0004"
down_revision = "20260226_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("latitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("longitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("location_display_name", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("projects", "location_display_name")
    op.drop_column("projects", "longitude")
    op.drop_column("projects", "latitude")
