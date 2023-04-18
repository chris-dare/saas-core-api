"""create_a_course

Revision ID: aa40dea29fbf
Revises: 8c5ed6379ac3
Create Date: 2023-01-21 22:00:38.781843

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'aa40dea29fbf'
down_revision = '8c5ed6379ac3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('uuid', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('event_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('summary', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('subscription_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('subscription_months', sa.Integer(), nullable=True),
    sa.Column('mode_of_delivery', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('keywords', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('application_deadline', sa.DateTime(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('instructor_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('organization_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('organization_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.uuid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('event_name', 'organization_id', name='_organization_event_name')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_instructor_name'), 'events', ['instructor_name'], unique=False)
    op.create_index(op.f('ix_events_organization_id'), 'events', ['organization_id'], unique=False)
    op.create_index(op.f('ix_events_organization_name'), 'events', ['organization_name'], unique=False)
    op.create_index(op.f('ix_events_user_id'), 'events', ['user_id'], unique=False)
    op.create_index(op.f('ix_events_uuid'), 'events', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_events_uuid'), table_name='events')
    op.drop_index(op.f('ix_events_user_id'), table_name='events')
    op.drop_index(op.f('ix_events_organization_name'), table_name='events')
    op.drop_index(op.f('ix_events_organization_id'), table_name='events')
    op.drop_index(op.f('ix_events_instructor_name'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
    # ### end Alembic commands ###
