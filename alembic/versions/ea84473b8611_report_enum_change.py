"""report enum change

Revision ID: ea84473b8611
Revises: 9e7e9cb652ae
Create Date: 2024-07-02 19:39:42.310538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ea84473b8611'
down_revision: Union[str, None] = '9e7e9cb652ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('registrations', 'reports_send_by')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('registrations', sa.Column('reports_send_by', postgresql.ENUM('COURIER', 'EMAIL', name='reportsentbyenum', create_type=False), autoincrement=False, nullable=True))
    # ### end Alembic commands ###