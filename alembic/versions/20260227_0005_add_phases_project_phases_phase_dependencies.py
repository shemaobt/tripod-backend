"""add phases project_phases and phase_dependencies

Revision ID: 20260227_0005
Revises: 20260226_0004
Create Date: 2026-02-27 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "20260227_0005"
down_revision = "20260226_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "phases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
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
    )

    op.create_table(
        "project_phases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("phase_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["phase_id"], ["phases.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "phase_id", name="uq_project_phase"),
    )
    op.create_index(
        op.f("ix_project_phases_project_id"),
        "project_phases",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_phases_phase_id"),
        "project_phases",
        ["phase_id"],
        unique=False,
    )

    op.create_table(
        "phase_dependencies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("phase_id", sa.String(length=36), nullable=False),
        sa.Column("depends_on_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["phase_id"], ["phases.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_id"], ["phases.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "phase_id", "depends_on_id", name="uq_phase_dependency"
        ),
    )
    op.create_index(
        op.f("ix_phase_dependencies_phase_id"),
        "phase_dependencies",
        ["phase_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_phase_dependencies_depends_on_id"),
        "phase_dependencies",
        ["depends_on_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_phase_dependencies_depends_on_id"),
        table_name="phase_dependencies",
    )
    op.drop_index(
        op.f("ix_phase_dependencies_phase_id"),
        table_name="phase_dependencies",
    )
    op.drop_table("phase_dependencies")

    op.drop_index(op.f("ix_project_phases_phase_id"), table_name="project_phases")
    op.drop_index(op.f("ix_project_phases_project_id"), table_name="project_phases")
    op.drop_table("project_phases")

    op.drop_table("phases")
