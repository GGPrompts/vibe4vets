"""merge_branches

Revision ID: 6b4c55d1bb4a
Revises: d6f1e4g3h901, e7h2g5i4j123
Create Date: 2026-01-18 20:21:26.775693

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "6b4c55d1bb4a"
down_revision: str | Sequence[str] | None = ("d6f1e4g3h901", "e7h2g5i4j123")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
