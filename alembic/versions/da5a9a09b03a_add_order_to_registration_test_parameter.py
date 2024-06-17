"""add order to registration test parameter

Revision ID: da5a9a09b03a
Revises: 4f35ae9f5281
Create Date: 2024-06-01 21:23:08.375196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da5a9a09b03a'
down_revision: Union[str, None] = '4f35ae9f5281'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('registration_test_parameters', sa.Column('order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('registration_test_parameters', 'order')
    # ### end Alembic commands ###