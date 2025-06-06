"""Add role column to users

Revision ID: f1bea931e084
Revises: 48144aafa96f
Create Date: 2025-05-17 11:48:03.308327

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1bea931e084'
down_revision = '48144aafa96f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Create new enum type with QUEUED status
    deploymentstatus = sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'QUEUED', name='deploymentstatus')
    deploymentstatus.create(op.get_bind(), checkfirst=True)
    
    # Update existing deployments table to use new enum
    op.alter_column('deployments', 'status',
                    existing_type=sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='deploymentstatus'),
                    type_=deploymentstatus,
                    existing_nullable=True)
    
    op.drop_table('user_organizations')
    op.add_column('clusters', sa.Column('total_cpu', sa.Float(), nullable=True))
    op.add_column('clusters', sa.Column('total_ram', sa.Float(), nullable=True))
    op.add_column('clusters', sa.Column('total_gpu', sa.Integer(), nullable=True))
    op.add_column('clusters', sa.Column('available_cpu', sa.Float(), nullable=True))
    op.add_column('clusters', sa.Column('available_ram', sa.Float(), nullable=True))
    op.add_column('clusters', sa.Column('available_gpu', sa.Integer(), nullable=True))
    op.drop_column('clusters', 'description')
    op.drop_column('clusters', 'resource_config')
    op.drop_column('clusters', 'status')
    op.drop_column('clusters', 'updated_at')
    op.drop_column('clusters', 'created_at')
    op.add_column('deployments', sa.Column('docker_image', sa.String(), nullable=True))
    op.add_column('deployments', sa.Column('priority', sa.Integer(), nullable=True))
    op.add_column('deployments', sa.Column('required_cpu', sa.Float(), nullable=True))
    op.add_column('deployments', sa.Column('required_ram', sa.Float(), nullable=True))
    op.add_column('deployments', sa.Column('required_gpu', sa.Integer(), nullable=True))
    op.add_column('deployments', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('deployments_user_id_fkey', 'deployments', 'users', ['user_id'], ['id'])
    op.drop_column('deployments', 'description')
    op.drop_column('deployments', 'scheduled_time')
    op.drop_column('deployments', 'updated_at')
    op.drop_column('deployments', 'resource_requirements')
    op.add_column('organizations', sa.Column('invite_code', sa.String(), nullable=True))
    op.drop_index('ix_organizations_name', table_name='organizations')
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_invite_code'), 'organizations', ['invite_code'], unique=True)
    op.drop_column('organizations', 'description')
    op.drop_column('organizations', 'created_at')
    op.drop_column('organizations', 'updated_at')
    # Create ENUM type before adding the column
    userrole = sa.Enum('ADMIN', 'DEVELOPER', 'VIEWER', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', userrole, nullable=True))
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key('users_organization_id_fkey', 'users', 'organizations', ['organization_id'], ['id'])
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_superuser')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint('users_organization_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'organization_id')
    op.drop_column('users', 'role')
    # Drop ENUM type after removing the column
    userrole = sa.Enum('ADMIN', 'DEVELOPER', 'VIEWER', name='userrole')
    userrole.drop(op.get_bind(), checkfirst=True)
    op.add_column('organizations', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('organizations', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('organizations', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_organizations_invite_code'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=True)
    op.drop_column('organizations', 'invite_code')
    op.add_column('deployments', sa.Column('resource_requirements', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('deployments', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('deployments', sa.Column('scheduled_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('deployments', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint('deployments_user_id_fkey', 'deployments', type_='foreignkey')
    op.drop_column('deployments', 'user_id')
    op.drop_column('deployments', 'required_gpu')
    op.drop_column('deployments', 'required_ram')
    op.drop_column('deployments', 'required_cpu')
    op.drop_column('deployments', 'priority')
    op.drop_column('deployments', 'docker_image')
    op.add_column('clusters', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('clusters', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('clusters', sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('clusters', sa.Column('resource_config', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('clusters', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('clusters', 'available_gpu')
    op.drop_column('clusters', 'available_ram')
    op.drop_column('clusters', 'available_cpu')
    op.drop_column('clusters', 'total_gpu')
    op.drop_column('clusters', 'total_ram')
    op.drop_column('clusters', 'total_cpu')
    op.create_table('user_organizations',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('organization_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='user_organizations_organization_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_organizations_user_id_fkey')
    )
    # ### end Alembic commands ### 