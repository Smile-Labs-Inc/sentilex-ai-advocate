from pydantic import BaseModel, EmailStr, Field, validator, field_validator
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

class LawyerCreate(LawyerBase):
    pass

class LawyerResponse(LawyerBase):
    id: int
    rating: float
    reviews_count: int

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