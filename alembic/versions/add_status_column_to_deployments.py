"""Add status column to deployments table

Revision ID: add_status_column_to_deployments
Revises: recreate_deploymentstatus_enum
Create Date: 2025-05-17 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_status_column_to_deployments'
down_revision = 'recreate_deploymentstatus_enum'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('deployments', sa.Column('status', sa.Enum('PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'QUEUED', name='deploymentstatus'), nullable=True))

def downgrade() -> None:
    op.drop_column('deployments', 'status') 