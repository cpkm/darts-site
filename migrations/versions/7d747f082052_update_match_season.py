"""update match season

Revision ID: 7d747f082052
Revises: e987b3608c74
Create Date: 2019-08-23 11:25:22.642057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d747f082052'
down_revision = 'e987b3608c74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('match', schema=None) as batch_op:
        batch_op.add_column(sa.Column('season_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_match_season_id_season'), 'season', ['season_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('match', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_match_season_id_season'), type_='foreignkey')
        batch_op.drop_column('season_id')

    # ### end Alembic commands ###