"""Add Index for datetime

Revision ID: c273825b18bd
Revises: 38887eae4aa6
Create Date: 2024-06-11 01:01:07.878143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c273825b18bd'
down_revision: Union[str, None] = '38887eae4aa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_coins_prices_timedate'), 'coins_prices', ['timedate'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_coins_prices_timedate'), table_name='coins_prices')
    # ### end Alembic commands ###
