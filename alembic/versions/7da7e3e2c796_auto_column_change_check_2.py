"""Auto Column Change Check 2

Revision ID: 7da7e3e2c796
Revises: d978132d96d7
Create Date: 2024-05-16 10:17:24.053902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7da7e3e2c796'
down_revision: Union[str, None] = 'd978132d96d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('samples_registration_id_fkey', 'samples', type_='foreignkey')
    op.drop_column('samples', 'registration_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('samples', sa.Column('registration_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('samples_registration_id_fkey', 'samples', 'registrations', ['registration_id'], ['id'])
    # ### end Alembic commands ###
