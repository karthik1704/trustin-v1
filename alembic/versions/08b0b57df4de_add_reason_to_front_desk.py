"""add reason to front desk

Revision ID: 08b0b57df4de
Revises: 000bfb47daf4
Create Date: 2024-07-05 20:14:14.332259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08b0b57df4de'
down_revision: Union[str, None] = '000bfb47daf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('frontdesks', sa.Column('reason', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('frontdesks', 'reason')
    # ### end Alembic commands ###
