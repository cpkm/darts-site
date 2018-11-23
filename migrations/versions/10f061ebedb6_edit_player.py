"""edit player

Revision ID: 10f061ebedb6
Revises: 24448892e1b1
Create Date: 2018-11-22 16:05:32.467877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10f061ebedb6'
down_revision = '24448892e1b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.drop_index('ix_player_email')
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=120), nullable=True))
        batch_op.create_index('ix_player_email', ['email'], unique=False)

    # ### end Alembic commands ###