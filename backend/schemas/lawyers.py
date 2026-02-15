from pydantic import BaseModel, EmailStr, Field, validator, field_validator, SecretStr
from typing import Optional, Literal
from datetime import datetime

class LawyerBase(BaseModel):
    name: str
    specialties: str
    experience_years: int
    email: EmailStr
    phone: str
    district: str
    availability: Optional[str] = "Available"

class LawyerRegister(BaseModel):
    """Schema for lawyer registration with authentication"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: SecretStr = Field(..., min_length=12, max_length=128)
    phone: str = Field(..., pattern=r'^\+?[\d\s\-\(\)]+$')
    district: str
    specialties: str
    experience_years: int = Field(..., ge=0, le=70)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        password = v.get_secret_value()
        
        if len(password) < 12:
            raise ValueError('Password must be at least 12 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValueError('Password must contain at least one special character')
        
        return v

class LawyerLogin(BaseModel):
    """Schema for lawyer login"""
    email: EmailStr
    password: SecretStr
    mfa_code: Optional[str] = Field(None, pattern=r'^\d{6}$')

class LawyerResponse(LawyerBase):
    """Basic lawyer response (public info)"""
    id: int
    rating: float
    reviews_count: int
    verification_status: str
    is_active: bool

    class Config:
        from_attributes = True

class LawyerProfileResponse(LawyerResponse):
    """Extended lawyer profile (for authenticated user viewing their own profile)"""
    is_email_verified: bool
    mfa_enabled: bool
    last_login: Optional[datetime] = None
    verification_step: int
    created_at: Optional[datetime] = None
    active_sessions: int
    
    class Config:
        from_attributes = True

class VerificationStep1(BaseModel):
    """Basic info - already collected at signup"""
    pass

class VerificationStep2(BaseModel):
    """Legal enrollment details"""
    sc_enrollment_number: str = Field(..., min_length=5, max_length=50)
    enrollment_year: int = Field(..., ge=1950, le=2026)
    law_college_reg_number: str = Field(..., min_length=5, max_length=50)
    
    @validator('enrollment_year')
    def validate_enrollment_year(cls, v):
        if v > datetime.now().year:
            raise ValueError("Enrollment year cannot be in the future")
        return v

class DocumentUploadResponse(BaseModel):
    """Response after successful document upload"""
    document_type: str
    url: str
    hash: str
    uploaded_at: datetime

class VerificationStep4(BaseModel):
    """Declaration acceptance"""
    declaration_accepted: Literal[True]  # Must be True

class DistrictLawyersResponse(BaseModel):
    """Response for lawyers grouped by district with coordinates"""
    district: str
    latitude: float
    longitude: float
    lawyer_count: int
    lawyers: list[LawyerResponse]
    
    class Config:
        from_attributes = True
    ip_address: str

class VerificationStatusResponse(BaseModel):
    """Current verification status"""
    verification_step: int
    verification_status: str
    can_proceed: bool
    rejection_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class AdminVerificationAction(BaseModel):
    """Admin approval/rejection"""
    action: str = Field(..., pattern="^(approve|reject)$")
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = Field(None, min_length=10)
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v, values):
        if values.get('action') == 'reject' and not v:
            raise ValueError("Rejection reason is mandatory when rejecting")
        return v

# ==========================================
# Authentication Schemas
# ==========================================

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: SecretStr
    new_password: SecretStr = Field(..., min_length=12, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validate new password strength"""
        password = v.get_secret_value()
        
        # Check if same as current
        if 'current_password' in values and values['current_password'].get_secret_value() == password:
            raise ValueError('New password must be different from current password')
        
        if len(password) < 12:
            raise ValueError('Password must be at least 12 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValueError('Password must contain at least one special character')
        
        return v

class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for resetting password with token"""
    token: str = Field(..., min_length=32)
    new_password: SecretStr = Field(..., min_length=12, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        password = v.get_secret_value()
        
        if len(password) < 12:
            raise ValueError('Password must be at least 12 characters long')
        
        if not any(c.isupper() for c in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValueError('Password must contain at least one special character')
        
        return v

class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., min_length=32)

class MFASetupResponse(BaseModel):
    """Response for MFA setup initiation"""
    secret: str
    qr_code_url: str
    backup_codes: list[str]

class MFAEnable(BaseModel):
    """Schema for enabling MFA"""
    verification_code: str = Field(..., pattern=r'^\d{6}$')

class MFAVerify(BaseModel):
    """Schema for MFA verification during login"""
    code: str = Field(..., pattern=r'^\d{6}$')

class SessionResponse(BaseModel):
    """Active session information"""
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