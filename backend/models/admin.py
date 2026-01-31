"""
Admin User Model for SentiLex AI Advocate

Handles admin and superadmin users with enhanced security features.
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, Enum
from sqlalchemy.sql import func
from database.config import Base
import enum
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class AdminRole(enum.Enum):
    """Admin role hierarchy"""
    ADMIN = "admin"                 # Standard admin access
    SUPERADMIN = "superadmin"       # Full system access


class Admin(Base):
    """
    Admin user model with authentication and security features.
    
    Features:
    - Role-based access (admin, superadmin)
    - Password authentication with bcrypt/argon2
    - Multi-factor authentication (TOTP)
    - Account status management
    - Login tracking and security
    """
    __tablename__ = "admins"

    # Primary Information
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(AdminRole, values_callable=lambda obj: [e.value for e in obj]), default=AdminRole.ADMIN, nullable=False)
    
    # Account Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(TIMESTAMP, nullable=True)
    
    # Password Security
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(TIMESTAMP, nullable=True)
    password_changed_at = Column(TIMESTAMP, nullable=True)
    password_history = Column(Text, nullable=True)  # JSON array of last 5 password hashes
    
    # Multi-Factor Authentication (Mandatory for admins)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP secret
    mfa_backup_codes = Column(Text, nullable=True)  # Encrypted JSON array of backup codes
    mfa_enabled_at = Column(TIMESTAMP, nullable=True)
    
    # Login Security
    last_login = Column(TIMESTAMP, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 support
    last_login_user_agent = Column(Text, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(TIMESTAMP, nullable=True)
    
    # Session Management
    active_sessions = Column(Integer, default=0, nullable=False)
    max_concurrent_sessions = Column(Integer, default=3, nullable=False)
    
    # Audit Trail
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    created_by_admin_id = Column(Integer, nullable=True)  # Which admin created this account
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=True)
    updated_by_admin_id = Column(Integer, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete
    
    # Additional Notes
    notes = Column(Text, nullable=True)  # Internal admin notes
    
    def __repr__(self):
        return f"<Admin(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        if not self.locked_until:
            return False
        from datetime import datetime
        return datetime.utcnow() < self.locked_until
    
    @property
    def requires_mfa_setup(self) -> bool:
        """Check if admin needs to set up MFA (required for all admins)"""
        return not self.mfa_enabled
    
    @property
    def is_superadmin(self) -> bool:
        """Check if user has superadmin privileges"""
        return self.role == AdminRole.SUPERADMIN

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminProfile(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True