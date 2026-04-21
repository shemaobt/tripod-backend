"""add created_by_user_id to oc_storytellers

Revision ID: 20260420_0003
Revises: 20260420_0002
Create Date: 2026-04-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_0003"
down_revision: str | None = "20260420_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "oc_storytellers",
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
    )
    op.create_foreign_key(
        "oc_storytellers_created_by_user_id_fkey",
        "oc_storytellers",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_oc_storytellers_project_creator",
        "oc_storytellers",
        ["project_id", "created_by_user_id"],
    )

    op.execute(
        "UPDATE oc_storytellers "
        "SET created_by_user_id = external_acceptance_confirmed_by "
        "WHERE created_by_user_id IS NULL "
        "AND external_acceptance_confirmed_by IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index(
        "ix_oc_storytellers_project_creator", table_name="oc_storytellers"
    )
    op.drop_constraint(
        "oc_storytellers_created_by_user_id_fkey",
        "oc_storytellers",
        type_="foreignkey",
    )
    op.drop_column("oc_storytellers", "created_by_user_id")
