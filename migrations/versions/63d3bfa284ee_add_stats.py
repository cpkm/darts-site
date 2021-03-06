"""add stats

Revision ID: 63d3bfa284ee
Revises: 40eb035ae7c7
Create Date: 2018-11-28 16:15:10.880598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d3bfa284ee'
down_revision = '40eb035ae7c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player_season_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.Column('matches_played', sa.Integer(), nullable=True),
    sa.Column('matches_won', sa.Integer(), nullable=True),
    sa.Column('matches_lost', sa.Integer(), nullable=True),
    sa.Column('games_played', sa.Integer(), nullable=True),
    sa.Column('games_won', sa.Integer(), nullable=True),
    sa.Column('games_lost', sa.Integer(), nullable=True),
    sa.Column('total_stars', sa.Integer(), nullable=True),
    sa.Column('total_high_scores', sa.Integer(), nullable=True),
    sa.Column('total_low_scores', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], name=op.f('fk_player_season_stats_player_id_player')),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], name=op.f('fk_player_season_stats_season_id_season')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_player_season_stats'))
    )
    op.create_table('team_season_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.Column('matches_played', sa.Integer(), nullable=True),
    sa.Column('matches_won', sa.Integer(), nullable=True),
    sa.Column('matches_lost', sa.Integer(), nullable=True),
    sa.Column('games_played', sa.Integer(), nullable=True),
    sa.Column('games_won', sa.Integer(), nullable=True),
    sa.Column('total_stars', sa.Integer(), nullable=True),
    sa.Column('total_high_scores', sa.Integer(), nullable=True),
    sa.Column('total_low_scores', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], name=op.f('fk_team_season_stats_season_id_season')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_team_season_stats'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team_season_stats')
    op.drop_table('player_season_stats')
    # ### end Alembic commands ###
