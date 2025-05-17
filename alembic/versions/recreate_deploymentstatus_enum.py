"""Recreate deploymentstatus enum with QUEUED

Revision ID: recreate_deploymentstatus_enum
Revises: add_queued_to_deploymentstatus
Create Date: 2025-05-17 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'recreate_deploymentstatus_enum'
down_revision = 'add_queued_to_deploymentstatus'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create new enum type with all values including QUEUED
    deploymentstatus = sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'QUEUED', name='deploymentstatus')
    deploymentstatus.create(op.get_bind(), checkfirst=True)
    
    # Update the deployments table to use the new enum
    op.execute('ALTER TABLE deployments ALTER COLUMN status TYPE deploymentstatus USING status::text::deploymentstatus')

def downgrade() -> None:
    # Revert to the old enum type without QUEUED
    deploymentstatus = sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='deploymentstatus')
    deploymentstatus.create(op.get_bind(), checkfirst=True)
    
    # Update the deployments table to use the old enum
    op.execute('ALTER TABLE deployments ALTER COLUMN status TYPE deploymentstatus USING status::text::deploymentstatus') 