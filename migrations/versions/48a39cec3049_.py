"""empty message

Revision ID: 48a39cec3049
Revises: 3c300f7bbb2
Create Date: 2015-02-07 16:44:09.945357

"""

# revision identifiers, used by Alembic.
revision = '48a39cec3049'
down_revision = '3c300f7bbb2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('proposal_invite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('proposal_id', sa.Integer(), nullable=True),
    sa.Column('recipient', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'accepted', 'declined', name='invite_statuses'), nullable=True),
    sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('proposal_invite')
    ENUM(name="invite_statuses").drop(op.get_bind(), checkfirst=False)
    ### end Alembic commands ###
