"""sample updates3

Revision ID: aaedd508f90f
Revises: 2ef1f74c4616
Create Date: 2024-03-09 01:47:57.803923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaedd508f90f'
down_revision: Union[str, None] = '2ef1f74c4616'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('samples_assigned_to_fkey', 'samples', type_='foreignkey')
    op.create_foreign_key(None, 'samples', 'users', ['assigned_to'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'samples', type_='foreignkey')
    op.create_foreign_key('samples_assigned_to_fkey', 'samples', 'sample_status', ['assigned_to'], ['id'])
    # ### end Alembic commands ###
