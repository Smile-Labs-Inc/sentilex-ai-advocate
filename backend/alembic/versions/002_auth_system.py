"""Add authentication and security system

Revision ID: 002_auth_system
Revises: 001_add_verification
Create Date: 2026-01-29

This migration adds:
- Admin user model with MFA support
- Authentication fields to lawyers table
- Token blacklist for JWT revocation
- Login attempt tracking
- Active session management
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_auth_system'
down_revision = '001_add_verification'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add authentication and security tables and columns.
    """
    
    # Create admin role enum (checkfirst to avoid duplicate)
    from sqlalchemy.dialects.postgresql import ENUM
    admin_role_enum = ENUM('admin', 'superadmin', name='adminrole', create_type=False)
    admin_role_enum.create(op.get_bind(), checkfirst=True)
    
    # ==========================================
    # 1. CREATE ADMINS TABLE
    # ==========================================
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # Primary Information
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('role', admin_role_enum, nullable=False, server_default='admin'),
        
        # Account Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('email_verification_token', sa.String(255), nullable=True),
        sa.Column('email_verification_sent_at', sa.TIMESTAMP(), nullable=True),
        
        # Password Security
        sa.Column('password_reset_token', sa.String(255), nullable=True),
        sa.Column('password_reset_expires', sa.TIMESTAMP(), nullable=True),
        sa.Column('password_changed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('password_history', sa.Text(), nullable=True),
        
        # Multi-Factor Authentication
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('mfa_secret', sa.String(32), nullable=True),
        sa.Column('mfa_backup_codes', sa.Text(), nullable=True),
        sa.Column('mfa_enabled_at', sa.TIMESTAMP(), nullable=True),
        
        # Login Security
        sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('last_login_user_agent', sa.Text(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.TIMESTAMP(), nullable=True),
        
        # Session Management
        sa.Column('active_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_concurrent_sessions', sa.Integer(), nullable=False, server_default='3'),
        
        # Audit Trail
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        
        # Additional Notes
        sa.Column('notes', sa.Text(), nullable=True),
    )
    
    # Create indexes for admins table
    op.create_index('idx_admin_email', 'admins', ['email'])
    op.create_index('idx_admin_active', 'admins', ['is_active'])
    op.create_index('idx_admin_role', 'admins', ['role'])
    
    
    # ==========================================
    # 2. EXTEND LAWYERS TABLE WITH AUTH FIELDS
    # ==========================================
    
    # Authentication & Security
    op.add_column('lawyers', sa.Column('password_hash', sa.String(255), nullable=True))
    op.add_column('lawyers', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('lawyers', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.add_column('lawyers', sa.Column('email_verification_sent_at', sa.TIMESTAMP(), nullable=True))
    
    # Password Security
    op.add_column('lawyers', sa.Column('password_reset_token', sa.String(255), nullable=True))
    op.add_column('lawyers', sa.Column('password_reset_expires', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('password_changed_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('password_history', sa.Text(), nullable=True))
    
    # Login Security
    op.add_column('lawyers', sa.Column('last_login', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('last_login_ip', sa.String(45), nullable=True))
    op.add_column('lawyers', sa.Column('last_login_user_agent', sa.Text(), nullable=True))
    op.add_column('lawyers', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('locked_until', sa.TIMESTAMP(), nullable=True))
    
    # Multi-Factor Authentication (Optional for lawyers)
    op.add_column('lawyers', sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('mfa_secret', sa.String(32), nullable=True))
    op.add_column('lawyers', sa.Column('mfa_backup_codes', sa.Text(), nullable=True))
    op.add_column('lawyers', sa.Column('mfa_enabled_at', sa.TIMESTAMP(), nullable=True))
    
    # Session Management
    op.add_column('lawyers', sa.Column('active_sessions', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('max_concurrent_sessions', sa.Integer(), nullable=False, server_default='5'))
    
    # Create indexes for lawyers auth fields
    op.create_index('idx_lawyer_email_verified', 'lawyers', ['is_email_verified'])
    op.create_index('idx_lawyer_active', 'lawyers', ['is_active'])
    
    
    # ==========================================
    # 3. CREATE TOKEN BLACKLIST TABLE
    # ==========================================
    op.create_table(
        'token_blacklist',
        sa.Column('jti', sa.String(36), primary_key=True),
        sa.Column('token_type', sa.String(10), nullable=False),
        
        # User Information
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_type', sa.String(10), nullable=False),
        
        # Blacklist Details
        sa.Column('blacklisted_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('reason', sa.String(50), nullable=False),
        
        # Additional Context
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
    )
    
    # Create indexes for token blacklist
    op.create_index('idx_token_user', 'token_blacklist', ['user_id', 'user_type'])
    op.create_index('idx_token_expires', 'token_blacklist', ['expires_at'])
    
    
    # ==========================================
    # 4. CREATE LOGIN ATTEMPTS TABLE
    # ==========================================
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # User Information
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('user_type', sa.String(10), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        
        # Attempt Details
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('attempted_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        
        # Network Information
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        
        # Failure Details
        sa.Column('failure_reason', sa.String(100), nullable=True),
        
        # Additional Context
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('is_suspicious', sa.Boolean(), nullable=False, server_default='0'),
    )
    
    # Create indexes for login attempts
    op.create_index('idx_login_email', 'login_attempts', ['email'])
    op.create_index('idx_login_ip', 'login_attempts', ['ip_address'])
    op.create_index('idx_login_attempted', 'login_attempts', ['attempted_at'])
    op.create_index('idx_login_email_time', 'login_attempts', ['email', 'attempted_at'])
    op.create_index('idx_login_ip_time', 'login_attempts', ['ip_address', 'attempted_at'])
    op.create_index('idx_login_user_time', 'login_attempts', ['user_id', 'attempted_at'])
    
    
    # ==========================================
    # 5. CREATE ACTIVE SESSIONS TABLE
    # ==========================================
    op.create_table(
        'active_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # Token Identification
        sa.Column('jti', sa.String(36), nullable=False, unique=True),
        
        # User Information
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_type', sa.String(10), nullable=False),
        
        # Session Details
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        
        # Device Information
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('os', sa.String(50), nullable=True),
        
        # Location (Optional)
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        
        # Session Context
        sa.Column('login_method', sa.String(20), nullable=True),
    )
    
    # Create indexes for active sessions
    op.create_index('idx_session_jti', 'active_sessions', ['jti'])
    op.create_index('idx_session_user', 'active_sessions', ['user_id', 'user_type'])
    op.create_index('idx_session_user_active', 'active_sessions', ['user_id', 'user_type', 'is_active'])
    op.create_index('idx_session_expires', 'active_sessions', ['expires_at'])


def downgrade() -> None:
    """
    Remove authentication and security tables and columns.
    """
    
    # Drop active sessions table
    op.drop_index('idx_session_expires', 'active_sessions')
    op.drop_index('idx_session_user_active', 'active_sessions')
    op.drop_index('idx_session_user', 'active_sessions')
    op.drop_index('idx_session_jti', 'active_sessions')
    op.drop_table('active_sessions')
    
    # Drop login attempts table
    op.drop_index('idx_login_user_time', 'login_attempts')
    op.drop_index('idx_login_ip_time', 'login_attempts')
    op.drop_index('idx_login_email_time', 'login_attempts')
    op.drop_index('idx_login_attempted', 'login_attempts')
    op.drop_index('idx_login_ip', 'login_attempts')
    op.drop_index('idx_login_email', 'login_attempts')
    op.drop_table('login_attempts')
    
    # Drop token blacklist table
    op.drop_index('idx_token_expires', 'token_blacklist')
    op.drop_index('idx_token_user', 'token_blacklist')
    op.drop_table('token_blacklist')
    
    # Remove lawyers auth columns
    op.drop_index('idx_lawyer_active', 'lawyers')
    op.drop_index('idx_lawyer_email_verified', 'lawyers')
    
    op.drop_column('lawyers', 'max_concurrent_sessions')
    op.drop_column('lawyers', 'active_sessions')
    op.drop_column('lawyers', 'mfa_enabled_at')
    op.drop_column('lawyers', 'mfa_backup_codes')
    op.drop_column('lawyers', 'mfa_secret')
    op.drop_column('lawyers', 'mfa_enabled')
    op.drop_column('lawyers', 'locked_until')
    op.drop_column('lawyers', 'failed_login_attempts')
    op.drop_column('lawyers', 'last_login_user_agent')
    op.drop_column('lawyers', 'last_login_ip')
    op.drop_column('lawyers', 'last_login')
    op.drop_column('lawyers', 'password_history')
    op.drop_column('lawyers', 'password_changed_at')
    op.drop_column('lawyers', 'password_reset_expires')
    op.drop_column('lawyers', 'password_reset_token')
    op.drop_column('lawyers', 'email_verification_sent_at')
    op.drop_column('lawyers', 'email_verification_token')
    op.drop_column('lawyers', 'is_email_verified')
    op.drop_column('lawyers', 'is_active')
    op.drop_column('lawyers', 'password_hash')
    
    # Drop admins table
    op.drop_index('idx_admin_role', 'admins')
    op.drop_index('idx_admin_active', 'admins')
    op.drop_index('idx_admin_email', 'admins')
    op.drop_table('admins')
    
    # Drop admin role enum
    admin_role_enum = sa.Enum('admin', 'superadmin', name='adminrole')
    admin_role_enum.drop(op.get_bind(), checkfirst=True)
