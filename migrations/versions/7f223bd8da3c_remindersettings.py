"""remindersettings

Revision ID: 7f223bd8da3c
Revises: b0239413c641
Create Date: 2019-09-19 08:55:46.132043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f223bd8da3c'
down_revision = 'b0239413c641'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reminder_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=64), nullable=True),
    sa.Column('days_in_advance', sa.Integer(), nullable=True),
    sa.Column('time_of_day', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_reminder_settings'))
    )
    with op.batch_alter_table('reminder_settings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reminder_settings_category'), ['category'], unique=False)

    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_index('ix_team_address')
        batch_op.create_index(batch_op.f('ix_team_address'), ['address'], unique=False)
        batch_op.drop_index('ix_team_home_location')
        batch_op.create_index(batch_op.f('ix_team_home_location'), ['home_location'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_team_home_location'))
        batch_op.create_index('ix_team_home_location', ['home_location'], unique=1)
        batch_op.drop_index(batch_op.f('ix_team_address'))
        batch_op.create_index('ix_team_address', ['address'], unique=1)

    with op.batch_alter_table('reminder_settings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reminder_settings_category'))

    op.drop_table('reminder_settings')
    # ### end Alembic commands ###
