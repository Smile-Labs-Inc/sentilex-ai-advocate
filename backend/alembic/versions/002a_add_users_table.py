"""Add users table

Revision ID: 002a_add_users_table
Revises: 002_auth_system
Create Date: 2026-02-04 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002a_add_users_table'
down_revision = '002_auth_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user role enum (only if it doesn't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('user', 'lawyer', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create language preference enum (only if it doesn't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE language_preference AS ENUM ('si', 'ta', 'en');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('oauth_provider', sa.String(length=20), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('role', postgresql.ENUM('user', 'lawyer', 'admin', name='user_role', create_type=False), nullable=True, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('mfa_secret', sa.String(length=32), nullable=True),
        sa.Column('mfa_backup_codes', sa.Text(), nullable=True),
        sa.Column('mfa_enabled_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_login_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('locked_until', sa.TIMESTAMP(), nullable=True),
        sa.Column('password_changed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('password_history', sa.Text(), nullable=True),
        sa.Column('preferred_language', postgresql.ENUM('si', 'ta', 'en', name='language_preference', create_type=False), nullable=True, server_default='en'),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('profile_completed', sa.Boolean(), nullable=True, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Note: We don't drop the enums here as they may be used by other tables
    # If needed, manually drop with: DROP TYPE IF EXISTS user_role, language_preference;
