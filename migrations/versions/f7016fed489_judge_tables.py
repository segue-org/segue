"""creates tables for judge, tournament and match

Revision ID: f7016fed489
Revises: 3f7a730da6dc
Create Date: 2015-06-01 00:48:06.813274

"""

# revision identifiers, used by Alembic.
revision = 'f7016fed489'
down_revision = '3f7a730da6dc'

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import ENUM

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tournament',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('current_round', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('selection', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('open', 'closed', name='tournament_statuses'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('judge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.String(length=64), nullable=True),
    sa.Column('votes', sa.Integer(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournament.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('result', sa.Enum('player1', 'player2', 'tie', name='match_results'), nullable=True),
    sa.Column('round', sa.Integer(), nullable=True),
    sa.Column('judge_id', sa.Integer(), nullable=True),
    sa.Column('player2_id', sa.Integer(), nullable=True),
    sa.Column('player1_id', sa.Integer(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['judge_id'], ['judge.id'], ),
    sa.ForeignKeyConstraint(['player1_id'], ['proposal.id'], ),
    sa.ForeignKeyConstraint(['player2_id'], ['proposal.id'], ),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournament.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('match')
    op.drop_table('judge')
    op.drop_table('tournament')
    ENUM(name="match_results").drop(op.get_bind(), checkfirst=False)
    ENUM(name="tournament_statuses").drop(op.get_bind(), checkfirst=False)
    ### end Alembic commands ###
