"""languages table and project association

Revision ID: 20260226_0003
Revises: 20260226_0002
Create Date: 2026-02-26 00:00:00.000000

"""

import uuid

import sqlalchemy as sa
from alembic import op


revision = "20260226_0003"
down_revision = "20260226_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "languages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_languages_code"), "languages", ["code"], unique=True)

    op.add_column(
        "projects",
        sa.Column("language_id", sa.String(length=36), nullable=True),
    )

    conn = op.get_bind()
    distinct = conn.execute(
        sa.text("SELECT DISTINCT language, code FROM projects")
    ).fetchall()
    for name, code in distinct:
        lang_id = str(uuid.uuid4())
        conn.execute(
            sa.text(
                "INSERT INTO languages (id, name, code, created_at) "
                "VALUES (:id, :name, :code, now())"
            ),
            {"id": lang_id, "name": name, "code": code},
        )
        conn.execute(
            sa.text(
                "UPDATE projects SET language_id = :lang_id "
                "WHERE language = :name AND code = :code"
            ),
            {"lang_id": lang_id, "name": name, "code": code},
        )

    op.alter_column(
        "projects",
        "language_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_projects_language_id",
        "projects",
        "languages",
        ["language_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        op.f("ix_projects_language_id"),
        "projects",
        ["language_id"],
        unique=False,
    )

    op.drop_index(op.f("ix_projects_code"), table_name="projects")
    op.drop_column("projects", "code")
    op.drop_column("projects", "language")


def downgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("language", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("code", sa.String(length=3), nullable=True),
    )

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT p.id, l.name, l.code FROM projects p "
            "JOIN languages l ON p.language_id = l.id"
        )
    ).fetchall()
    for project_id, name, code in rows:
        conn.execute(
            sa.text(
                "UPDATE projects SET language = :name, code = :code WHERE id = :id"
            ),
            {"id": project_id, "name": name, "code": code},
        )

    op.alter_column(
        "projects",
        "language",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "projects",
        "code",
        existing_type=sa.String(length=3),
        nullable=False,
    )
    op.create_index(op.f("ix_projects_code"), "projects", ["code"], unique=False)

    op.drop_constraint(
        "fk_projects_language_id",
        "projects",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_projects_language_id"), table_name="projects")
    op.drop_column("projects", "language_id")

    op.drop_index(op.f("ix_languages_code"), table_name="languages")
    op.drop_table("languages")
