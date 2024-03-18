"""menus changes

Revision ID: 960b0e08027c
Revises: fff5e947eccb
Create Date: 2024-03-15 23:15:45.858208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '960b0e08027c'
down_revision: Union[str, None] = 'fff5e947eccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('samples', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'samples', 'testingparameters', ['department_id'], ['id'])
    op.drop_column('samples', 'department')
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'testingparameters', ['department_id'], ['id'])
    op.drop_column('users', 'department')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('department', postgresql.ENUM('MECH', 'MICRO', name='department'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'department_id')
    op.add_column('samples', sa.Column('department', postgresql.ENUM('MECH', 'MICRO', name='department'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'samples', type_='foreignkey')
    op.drop_column('samples', 'department_id')
    # ### end Alembic commands ###
