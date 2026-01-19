"""merge_branches

Revision ID: 6b4c55d1bb4a
Revises: d6f1e4g3h901, e7h2g5i4j123
Create Date: 2026-01-18 20:21:26.775693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b4c55d1bb4a'
down_revision: Union[str, Sequence[str], None] = ('d6f1e4g3h901', 'e7h2g5i4j123')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
