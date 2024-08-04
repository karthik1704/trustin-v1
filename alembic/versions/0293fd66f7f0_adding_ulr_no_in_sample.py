"""adding ulr no in sample 

Revision ID: 0293fd66f7f0
Revises: 2db0f00a4d04
Create Date: 2024-08-03 12:18:48.538320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0293fd66f7f0'
down_revision: Union[str, None] = '2db0f00a4d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('samples', sa.Column('ulr_no', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('samples', 'ulr_no')
    # ### end Alembic commands ###
