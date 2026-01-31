"""Add MFA and password security fields

Revision ID: 003_add_mfa_password
Revises: 002_auth_system
Create Date: 2026-01-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_mfa_password'
down_revision = '002_auth_system'
branch_labels = None
depends_on = None


def upgrade():
    # Check if users table exists before adding columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        # Add MFA and password security fields to users table
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'mfa_secret' not in existing_columns:
            op.add_column('users', sa.Column('mfa_secret', sa.String(length=32), nullable=True))
        if 'mfa_backup_codes' not in existing_columns:
            op.add_column('users', sa.Column('mfa_backup_codes', sa.Text(), nullable=True))
        if 'mfa_enabled_at' not in existing_columns:
            op.add_column('users', sa.Column('mfa_enabled_at', sa.TIMESTAMP(), nullable=True))
        if 'locked_until' not in existing_columns:
            op.add_column('users', sa.Column('locked_until', sa.TIMESTAMP(), nullable=True))
        if 'password_changed_at' not in existing_columns:
            op.add_column('users', sa.Column('password_changed_at', sa.TIMESTAMP(), nullable=True))
        if 'password_history' not in existing_columns:
            op.add_column('users', sa.Column('password_history', sa.Text(), nullable=True))
    
    # Add fields to lawyers table if they don't exist
    if 'lawyers' in tables:
        existing_columns = [col['name'] for col in inspector.get_columns('lawyers')]
        
        if 'password_history' not in existing_columns:
            op.add_column('lawyers', sa.Column('password_history', sa.Text(), nullable=True))
        if 'password_changed_at' not in existing_columns:
            op.add_column('lawyers', sa.Column('password_changed_at', sa.TIMESTAMP(), nullable=True))
        if 'locked_until' not in existing_columns:
            op.add_column('lawyers', sa.Column('locked_until', sa.TIMESTAMP(), nullable=True))
        if 'mfa_secret' not in existing_columns:
            op.add_column('lawyers', sa.Column('mfa_secret', sa.String(length=32), nullable=True))
        if 'mfa_backup_codes' not in existing_columns:
            op.add_column('lawyers', sa.Column('mfa_backup_codes', sa.Text(), nullable=True))
        if 'mfa_enabled_at' not in existing_columns:
            op.add_column('lawyers', sa.Column('mfa_enabled_at', sa.TIMESTAMP(), nullable=True))


def downgrade():
    # Check if tables exist before dropping columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # Remove MFA and password security fields from users table
    if 'users' in tables:
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'password_history' in existing_columns:
            op.drop_column('users', 'password_history')
        if 'password_changed_at' in existing_columns:
            op.drop_column('users', 'password_changed_at')
        if 'locked_until' in existing_columns:
            op.drop_column('users', 'locked_until')
        if 'mfa_enabled_at' in existing_columns:
            op.drop_column('users', 'mfa_enabled_at')
        if 'mfa_backup_codes' in existing_columns:
            op.drop_column('users', 'mfa_backup_codes')
        if 'mfa_secret' in existing_columns:
            op.drop_column('users', 'mfa_secret')
    
    # Remove from lawyers table
    if 'lawyers' in tables:
        existing_columns = [col['name'] for col in inspector.get_columns('lawyers')]
        
        if 'mfa_enabled_at' in existing_columns:
            op.drop_column('lawyers', 'mfa_enabled_at')
        if 'mfa_backup_codes' in existing_columns:
            op.drop_column('lawyers', 'mfa_backup_codes')
        if 'mfa_secret' in existing_columns:
            op.drop_column('lawyers', 'mfa_secret')
        if 'locked_until' in existing_columns:
            op.drop_column('lawyers', 'locked_until')
        if 'password_changed_at' in existing_columns:
            op.drop_column('lawyers', 'password_changed_at')
        if 'password_history' in existing_columns:
            op.drop_column('lawyers', 'password_history')
