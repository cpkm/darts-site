"""UserSettings

Revision ID: e4c82ae4d694
Revises: adf92ce97809
Create Date: 2019-11-29 14:13:50.587417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4c82ae4d694'
down_revision = 'adf92ce97809'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('email_reminders', sa.Boolean(), nullable=True),
    sa.Column('email_summary', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_user_settings_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_settings'))
    )
    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_settings_email_reminders'), ['email_reminders'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_settings_email_summary'), ['email_summary'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_settings_email_summary'))
        batch_op.drop_index(batch_op.f('ix_user_settings_email_reminders'))

    op.drop_table('user_settings')
    # ### end Alembic commands ###
