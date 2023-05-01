"""subaccounts

Revision ID: 7c220088e286
Revises: 81916dc4793f
Create Date: 2023-05-01 18:27:55.112539

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '7c220088e286'
down_revision = '81916dc4793f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subaccounts',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('uuid', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('owner_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('organization_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('business_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('settlement_bank_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('account_number', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('percentage_charge', sa.DECIMAL(precision=5, scale=2), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('primary_contact_email', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('primary_contact_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('primary_contact_phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.uuid'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subaccounts_business_name'), 'subaccounts', ['business_name'], unique=False)
    op.create_index(op.f('ix_subaccounts_id'), 'subaccounts', ['id'], unique=False)
    op.create_index(op.f('ix_subaccounts_organization_id'), 'subaccounts', ['organization_id'], unique=False)
    op.create_index(op.f('ix_subaccounts_primary_contact_email'), 'subaccounts', ['primary_contact_email'], unique=False)
    op.create_index(op.f('ix_subaccounts_primary_contact_name'), 'subaccounts', ['primary_contact_name'], unique=False)
    op.create_index(op.f('ix_subaccounts_primary_contact_phone'), 'subaccounts', ['primary_contact_phone'], unique=False)
    op.create_index(op.f('ix_subaccounts_owner_id'), 'subaccounts', ['owner_id'], unique=False)
    op.create_index(op.f('ix_subaccounts_uuid'), 'subaccounts', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_subaccounts_uuid'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_owner_id'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_primary_contact_phone'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_primary_contact_name'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_primary_contact_email'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_organization_id'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_id'), table_name='subaccounts')
    op.drop_index(op.f('ix_subaccounts_business_name'), table_name='subaccounts')
    op.drop_table('subaccounts')
    # ### end Alembic commands ###