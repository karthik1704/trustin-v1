"""merge heads

Revision ID: 741d986befb4
Revises: 727e24d57942, bdb7e7f3d6c2
Create Date: 2024-08-01 12:31:05.717408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '741d986befb4'
down_revision: Union[str, None] = ('727e24d57942', 'bdb7e7f3d6c2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
