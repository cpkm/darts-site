"""team season stats

Revision ID: ce85b497ec3d
Revises: 13a6ac4849b3
Create Date: 2018-11-27 17:04:42.499735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce85b497ec3d'
down_revision = '13a6ac4849b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team_season_statistics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.Column('matches_played', sa.Integer(), nullable=False),
    sa.Column('matches_won', sa.Integer(), nullable=False),
    sa.Column('matches_lost', sa.Integer(), nullable=False),
    sa.Column('games_played', sa.Integer(), nullable=False),
    sa.Column('games_won', sa.Integer(), nullable=False),
    sa.Column('total_stars', sa.Integer(), nullable=False),
    sa.Column('total_high_scores', sa.Integer(), nullable=False),
    sa.Column('total_low_scores', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], name=op.f('fk_team_season_statistics_season_id_season')),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], name=op.f('fk_team_season_statistics_team_id_team')),
    sa.PrimaryKeyConstraint('id', 'matches_played', 'matches_won', 'matches_lost', 'games_played', 'games_won', 'total_stars', 'total_high_scores', 'total_low_scores', name=op.f('pk_team_season_statistics'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_season_statistics')
    # ### end Alembic commands ###
