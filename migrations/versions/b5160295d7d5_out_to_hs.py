"""out to hs

Revision ID: b5160295d7d5
Revises: 5758066be55b
Create Date: 2019-09-01 11:20:49.569102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5160295d7d5'
down_revision = '5758066be55b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('high_score', schema=None) as batch_op:
        batch_op.add_column(sa.Column('out', sa.Boolean(), nullable=True))
        batch_op.create_index(batch_op.f('ix_high_score_out'), ['out'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('high_score', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_high_score_out'))
        batch_op.drop_column('out')

    # ### end Alembic commands ###
