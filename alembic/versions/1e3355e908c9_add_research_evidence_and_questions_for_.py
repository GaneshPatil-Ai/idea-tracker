"""Add research evidence and questions for Phase 6

Revision ID: 1e3355e908c9
Revises: 8a1164cf65dd
Create Date: 2026-10-07 03:24:42.386807

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1e3355e908c9'
down_revision: str | Sequence[str] | None = '8a1164cf65dd'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "research_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("idea_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column(
            "evidence_type",
            sa.Enum("ARTICLE", "VIDEO", "PODCAST", "DOCUMENT", "INTERVIEW", "WEBSITE", "STUDY", "OTHER", name="evidencetype"),
            nullable=False,
        ),
        sa.Column("author", sa.String(length=200), nullable=True),
        sa.Column("publication_date", sa.DateTime(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "research_questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("idea_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("research_questions")
    op.drop_table("research_evidence")
