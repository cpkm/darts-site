"""player season stats update

Revision ID: 13a6ac4849b3
Revises: 532d01f27de1
Create Date: 2018-11-27 17:02:54.059469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13a6ac4849b3'
down_revision = '532d01f27de1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player_season_statistics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('season_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_player_season_statistics_season_id_season'), 'season', ['season_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player_season_statistics', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_player_season_statistics_season_id_season'), type_='foreignkey')
        batch_op.drop_column('season_id')

    # ### end Alembic commands ###
