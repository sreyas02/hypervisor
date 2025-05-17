"""Add QUEUED to deploymentstatus enum

Revision ID: add_queued_to_deploymentstatus
Revises: f1bea931e084
Create Date: 2025-05-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_queued_to_deploymentstatus'
down_revision = 'f1bea931e084'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create a new enum type with QUEUED status
    deploymentstatus = sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'QUEUED', name='deploymentstatus')
    deploymentstatus.create(op.get_bind(), checkfirst=True)
    
    # Update existing deployments table to use new enum
    op.alter_column('deployments', 'status',
                    existing_type=sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='deploymentstatus'),
                    type_=deploymentstatus,
                    existing_nullable=True)

def downgrade() -> None:
    # Revert to the old enum type without QUEUED
    deploymentstatus = sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='deploymentstatus')
    deploymentstatus.create(op.get_bind(), checkfirst=True)
    
    op.alter_column('deployments', 'status',
                    existing_type=sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'QUEUED', name='deploymentstatus'),
                    type_=deploymentstatus,
                    existing_nullable=True) 