"""
Authentication Response Schemas

Common schemas for authentication responses (tokens, login, etc.)
"""

from pydantic import BaseModel, Field, EmailStr, SecretStr, validator
from typing import Optional, Literal
from datetime import datetime
import re

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================
class UserRegister(BaseModel):
    """user registration request"""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    preferred_language: str = Field(default="en", pattern="^(si|ta|en)$")
    district: Optional[str] = Field(None, max_length=50)

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class PasswordReset(BaseModel):
    """Password reset request (forgot password)"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class EmailVerification(BaseModel):
    """Email verification request"""
    token: str


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Response after token refresh"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenResponse(BaseModel):
    """Standard token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile response"""
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    email_verified: bool
    mfa_enabled: bool
    preferred_language: str
    district: Optional[str]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_type: Literal["user", "lawyer", "admin"]
    requires_mfa: bool = False
    mfa_enabled: bool = False
    
    # User info
    user_id: int
    email: str
    name: str
    role: Optional[str] = None  # For admins

class RegistrationResponse(BaseModel):
    """Response after successful registration"""
    message: str = "Registration successful. Please verify your email."
    user: UserProfile
    verification_sent: bool = True


class MFARequiredResponse(BaseModel):
    """Response when MFA verification is required"""
    message: str = "MFA verification required"
    requires_mfa: bool = True
    temp_token: str  # Temporary token to complete MFA flow


class LogoutResponse(BaseModel):
    """Response after logout"""
    message: str = "Successfully logged out"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PasswordResetEmailSentResponse(BaseModel):
    """Response after password reset email sent"""
    message: str = "If the email exists, a password reset link has been sent"
    email: str


class EmailVerificationSentResponse(BaseModel):
    """Response after verification email sent"""
    message: str = "Verification email sent"
    email: str

class SessionInfo(BaseModel):
    """Active session information"""
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True


class ActiveSessionsResponse(BaseModel):
    """Response with all active sessions"""
    sessions: list[SessionInfo]
    total: int


# ============================================================================
# MFA SCHEMAS
# ============================================================================

class MFASetupResponse(BaseModel):
    """Response for MFA setup initialization"""
    secret: str
    qr_code_url: str
    backup_codes: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code_url": "data:image/png;base64,iVBORw0KGgo...",
                "backup_codes": ["ABCD1234", "EFGH5678"]
            }
        }


class MFAEnable(BaseModel):
    """Request to enable MFA"""
    verification_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    
    @validator('verification_code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Verification code must contain only digits')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "verification_code": "123456"
            }
        }


class MFAVerify(BaseModel):
    """Request to verify MFA code during login"""
    temp_token: str = Field(..., description="Temporary token from login response")
    code: str = Field(..., min_length=6, max_length=8, description="6-digit TOTP code or 8-digit backup code")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @validator('code')
    def validate_code(cls, v):
        # Allow either 6-digit TOTP or 8-character backup code
        if len(v) == 6 and not v.isdigit():
            raise ValueError('TOTP code must be 6 digits')
        elif len(v) == 8 and not v.isalnum():
            raise ValueError('Backup code must be 8 alphanumeric characters')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "temp_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "code": "123456",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        }


class MFADisable(BaseModel):
    """Request to disable MFA"""
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "SecurePassword123!"
            }
        }


class MFAStatus(BaseModel):
    """MFA status response"""
    mfa_enabled: bool
    mfa_enabled_at: Optional[datetime] = None
    backup_codes_remaining: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "mfa_enabled": True,
                "mfa_enabled_at": "2024-01-15T10:30:00",
                "backup_codes_remaining": 8
            }
        }