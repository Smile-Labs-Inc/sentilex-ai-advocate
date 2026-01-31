from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# User Profile Completion Schemas
class UserProfileComplete(BaseModel):
    """Schema for completing user profile after OAuth registration"""
    preferred_language: str = Field(..., pattern="^(si|ta|en)$", description="Preferred language: si, ta, or en")
    district: str = Field(..., min_length=2, max_length=50, description="User's district")

class UserProfileCompleteResponse(BaseModel):
    message: str
    profile_completed: bool
    user_id: int
    
    class Config:
        from_attributes = True


# Lawyer Profile Completion Schemas
class LawyerProfileComplete(BaseModel):
    """Schema for completing lawyer profile after OAuth registration"""
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    specialties: str = Field(..., min_length=2, max_length=255, description="Legal specialties (comma-separated)")
    experience_years: int = Field(..., ge=0, le=70, description="Years of legal experience")
    district: str = Field(..., min_length=2, max_length=50, description="Primary district of practice")
    preferred_language: Optional[str] = Field("en", pattern="^(si|ta|en)$", description="Preferred language")

class LawyerProfileCompleteResponse(BaseModel):
    message: str
    profile_completed: bool
    lawyer_id: int
    needs_verification: bool = True
    
    class Config:
        from_attributes = True


# Profile Status Schemas
class ProfileStatus(BaseModel):
    """Check if user/lawyer profile is complete"""
    profile_completed: bool
    missing_fields: list[str] = []
    user_type: str  # "user" or "lawyer"
    
class OAuthRegistrationResponse(BaseModel):
    """Response after OAuth registration"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_type: str
    email: str
    profile_completed: bool
    redirect_url: str  # Where to redirect user (dashboard or profile-completion)
