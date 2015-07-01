"""added_discount_field_to_promocode

Revision ID: 368f04504df4
Revises: 5a11b40ca10d
Create Date: 2015-06-30 21:35:14.100554

"""

# revision identifiers, used by Alembic.
revision = '368f04504df4'
down_revision = '5a11b40ca10d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('promo_code', sa.Column('discount', sa.Numeric(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('promo_code', 'discount')
    ### end Alembic commands ###
