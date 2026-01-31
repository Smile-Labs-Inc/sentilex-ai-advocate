"""
Admin Authentication Schemas

Pydantic models for admin user authentication and management.
"""

from pydantic import BaseModel, EmailStr, Field, validator, SecretStr
from typing import Optional
from datetime import datetime


class AdminBase(BaseModel):
    """Base admin schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class AdminRegister(AdminBase):
    """Schema for admin registration (by superadmin only)"""
    password: SecretStr = Field(..., min_length=14, max_length=128)
    role: str = Field(default="admin", pattern="^(admin|superadmin)$")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength - stricter for admins"""
        password = v.get_secret_value()
        
        if len(password) < 14:
            raise ValueError('Admin password must be at least 14 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValueError('Password must contain at least one special character')
        
        # Check for at least 2 special characters (stricter)
        special_count = sum(1 for c in password if c in '!@#$%^&*()_+-=[]{}|;:,.<>?')
        if special_count < 2:
            raise ValueError('Admin password must contain at least two special characters')
        
        return v


class AdminLogin(BaseModel):
    """Schema for admin login"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class AdminResponse(AdminBase):
    """Admin response (safe to send to client)"""
    id: int
    role: str
    is_active: bool
    is_email_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    active_sessions: int
    
    class Config:
        from_attributes = True


class AdminUpdate(BaseModel):
    """Schema for updating admin details"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class AdminPasswordChange(BaseModel):
    """Schema for admin password change"""
    current_password: SecretStr
    new_password: SecretStr = Field(..., min_length=14, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validate new password strength"""
        password = v.get_secret_value()
        
        # Check if same as current
        if 'current_password' in values and values['current_password'].get_secret_value() == password:
            raise ValueError('New password must be different from current password')
        
        if len(password) < 14:
            raise ValueError('Admin password must be at least 14 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValueError('Password must contain at least one digit')
        
        special_count = sum(1 for c in password if c in '!@#$%^&*()_+-=[]{}|;:,.<>?')
        if special_count < 2:
            raise ValueError('Admin password must contain at least two special characters')
        
        return v


class AdminMFASetupResponse(BaseModel):
    """Response for admin MFA setup (mandatory)"""
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class AdminMFAEnable(BaseModel):
    """Schema for enabling MFA"""
    verification_code: str = Field(..., pattern=r'^\d{6}$')


class AdminSessionResponse(BaseModel):
    """Active admin session information"""
    id: int
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: str
    created_at: datetime
    last_activity: datetime
    is_current: bool = False
    
    class Config:
        from_attributes = True


class AdminListResponse(BaseModel):
    """Admin list item (for admin management)"""
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminProfile(BaseModel):
    """Admin user profile"""
    id: int
    email: str
    role: str
    is_active: bool
    mfa_enabled: bool
    mfa_enabled_at: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "admin@sentilex.ai",
                "role": "super_admin",
                "is_active": True,
                "mfa_enabled": True,
                "mfa_enabled_at": "2024-01-10T08:00:00",
                "created_at": "2024-01-01T00:00:00",
                "last_login_at": "2024-01-15T14:30:00"
            }
        }
