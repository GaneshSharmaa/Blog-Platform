"""initial schema

Revision ID: a0bfd01254b3
Revises: 0663d21b6b40
Create Date: 2026-08-04 11:54:26.159508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0bfd01254b3'
down_revision: Union[str, Sequence[str], None] = '0663d21b6b40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
