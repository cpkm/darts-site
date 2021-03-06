"""pss id

Revision ID: 825814fd56b1
Revises: ad2f7d267b33
Create Date: 2018-11-28 16:10:43.176920

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '825814fd56b1'
down_revision = 'ad2f7d267b33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player_season_stats', schema=None) as batch_op:
        batch_op.alter_column('games_lost',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('games_played',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('games_won',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_lost',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_played',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_won',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_high_scores',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_low_scores',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_stars',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('team_season_stats', schema=None) as batch_op:
        batch_op.alter_column('games_played',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('games_won',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_lost',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_played',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('matches_won',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_high_scores',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_low_scores',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('total_stars',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team_season_stats', schema=None) as batch_op:
        batch_op.alter_column('total_stars',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('total_low_scores',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('total_high_scores',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_won',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_played',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_lost',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('games_won',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('games_played',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('player_season_stats', schema=None) as batch_op:
        batch_op.alter_column('total_stars',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('total_low_scores',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('total_high_scores',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_won',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_played',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('matches_lost',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('games_won',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('games_played',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('games_lost',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
