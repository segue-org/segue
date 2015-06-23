"""boleto our number should be big integer

Revision ID: 3c8d450cb51f
Revises: 1f43fb8f5121
Create Date: 2015-06-23 15:08:37.882334

"""

# revision identifiers, used by Alembic.
revision = '3c8d450cb51f'
down_revision = '1f43fb8f5121'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(table_name='payment', column_name='bo_our_number', type_ = sa.BigInteger())

def downgrade():
    op.alter_column(table_name='payment', column_name='bo_our_number', type_ = sa.Integer())
