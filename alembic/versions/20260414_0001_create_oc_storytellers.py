"""create oc_storytellers and link to oc_recordings

Revision ID: 20260414_0001
Revises: 20260413_0001
Create Date: 2026-04-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260414_0001"
down_revision: str | None = "20260413_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oc_storytellers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("sex", sa.String(length=10), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("dialect", sa.Text(), nullable=True),
        sa.Column(
            "external_acceptance_confirmed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "external_acceptance_confirmed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("external_acceptance_confirmed_by", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["external_acceptance_confirmed_by"], ["users.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_oc_storytellers_project_id", "oc_storytellers", ["project_id"]
    )

    op.add_column(
        "oc_recordings",
        sa.Column("storyteller_id", sa.String(length=36), nullable=True),
    )
    op.create_foreign_key(
        "oc_recordings_storyteller_id_fkey",
        "oc_recordings",
        "oc_storytellers",
        ["storyteller_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_oc_recordings_storyteller_id", "oc_recordings", ["storyteller_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_oc_recordings_storyteller_id", table_name="oc_recordings")
    op.drop_constraint(
        "oc_recordings_storyteller_id_fkey", "oc_recordings", type_="foreignkey"
    )
    op.drop_column("oc_recordings", "storyteller_id")
    op.drop_index("ix_oc_storytellers_project_id", table_name="oc_storytellers")
    op.drop_table("oc_storytellers")
