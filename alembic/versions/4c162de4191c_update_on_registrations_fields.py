"""update on registrations fields

Revision ID: 4c162de4191c
Revises: 76fe7fc87f47
Create Date: 2024-07-01 20:04:18.710069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c162de4191c'
down_revision: Union[str, None] = '76fe7fc87f47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('registrations', sa.Column('full_address', sa.Text(), nullable=True))
    op.add_column('registrations', sa.Column('no_of_batches', sa.Integer(), nullable=False))
    op.alter_column('registrations', 'branch_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('registrations', 'customer_address_line1')
    op.drop_column('registrations', 'pincode_no')
    op.drop_column('registrations', 'state')
    op.drop_column('registrations', 'nabl_logo')
    op.drop_column('registrations', 'city')
    op.drop_column('registrations', 'customer_address_line2')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('registrations', sa.Column('customer_address_line2', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('registrations', sa.Column('city', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('registrations', sa.Column('nabl_logo', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('registrations', sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('registrations', sa.Column('pincode_no', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('registrations', sa.Column('customer_address_line1', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.alter_column('registrations', 'branch_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('registrations', 'no_of_batches')
    op.drop_column('registrations', 'full_address')
    # ### end Alembic commands ###
