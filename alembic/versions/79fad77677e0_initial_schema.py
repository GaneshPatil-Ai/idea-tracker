"""initial_schema

Revision ID: 79fad77677e0
Revises:
Create Date: 2026-10-06 19:18:24.351343

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '79fad77677e0'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
