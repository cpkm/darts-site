"""modify user

Revision ID: 53ec60ee98bb
Revises: f4f4ca2e0950
Create Date: 2019-06-14 16:28:47.060074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53ec60ee98bb'
down_revision = 'f4f4ca2e0950'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registered_on', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('verified_on', sa.Date(), nullable=True))
        batch_op.create_index(batch_op.f('ix_user_registered_on'), ['registered_on'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_verified'), ['verified'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_verified_on'), ['verified_on'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_verified_on'))
        batch_op.drop_index(batch_op.f('ix_user_verified'))
        batch_op.drop_index(batch_op.f('ix_user_registered_on'))
        batch_op.drop_column('verified_on')
        batch_op.drop_column('verified')
        batch_op.drop_column('registered_on')

    # ### end Alembic commands ###