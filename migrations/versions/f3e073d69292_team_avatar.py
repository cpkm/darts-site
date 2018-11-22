"""team avatar

Revision ID: f3e073d69292
Revises: 03b480c93aa2
Create Date: 2018-11-21 16:59:34.050365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3e073d69292'
down_revision = '03b480c93aa2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_index('ix_team_name')
        batch_op.create_index(batch_op.f('ix_team_name'), ['name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_team_name'))
        batch_op.create_index('ix_team_name', ['name'], unique=False)

    # ### end Alembic commands ###
