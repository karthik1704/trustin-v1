"""order to sample test param

Revision ID: 198196a0b767
Revises: b4a560dc3088
Create Date: 2024-03-25 17:36:50.767590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '198196a0b767'
down_revision: Union[str, None] = 'b4a560dc3088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sample_test_parameters', sa.Column('order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sample_test_parameters', 'order')
    # ### end Alembic commands ###
