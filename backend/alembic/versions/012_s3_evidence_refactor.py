"""s3 evidence refactor

Revision ID: 012_s3_evidence_refactor
Revises: 011_add_occurrences
Create Date: 2026-02-09 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_s3_evidence_refactor'
down_revision = '011_add_occurrences'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migrate Evidence table from local file storage to S3 storage.
    
    Changes:
    - Remove file_path column (local disk path)
    - Add file_key column (S3 object key)
    - Add file_hash column (SHA-256 hash for forensic audit)
    """
    # Add new columns
    op.add_column('evidence', sa.Column('file_key', sa.String(length=500), nullable=True))
    op.add_column('evidence', sa.Column('file_hash', sa.String(length=64), nullable=True))
    
    # Note: We set nullable=True initially to allow migration of existing data
    # In a production scenario, you would:
    # 1. Migrate existing files to S3 and populate file_key and file_hash
    # 2. Then alter columns to be NOT NULL
    
    # For new installations or if no existing data needs migration:
    # Make columns NOT NULL after data migration (uncomment if needed)
    # op.alter_column('evidence', 'file_key', nullable=False)
    # op.alter_column('evidence', 'file_hash', nullable=False)
    
    # Drop old column
    op.drop_column('evidence', 'file_path')


def downgrade() -> None:
    """
    Rollback to local file storage.
    
    WARNING: This will lose S3 file references!
    """
    # Add back file_path column
    op.add_column('evidence', sa.Column('file_path', sa.String(length=500), nullable=True))
    
    # Drop S3 columns
    op.drop_column('evidence', 'file_hash')
    op.drop_column('evidence', 'file_key')
