"""Add uniq constraint

Revision ID: 5771c18f5aec
Revises: afd437be7d8a
Create Date: 2024-06-11 04:46:08.656087

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5771c18f5aec'
down_revision: Union[str, None] = 'afd437be7d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('coin_alert_type', 'alerts', ['coin_id', 'alert_type', 'threshold_price'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('coin_alert_type', 'alerts', type_='unique')
    # ### end Alembic commands ###