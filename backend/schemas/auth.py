"""
Authentication Response Schemas

Common schemas for authentication responses (tokens, login, etc.)
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


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


class LoginResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_type: Literal["lawyer", "admin"]
    requires_mfa: bool = False
    mfa_enabled: bool = False
    
    # User info
    user_id: int
    email: str
    name: str
    role: Optional[str] = None  # For admins


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


class RegistrationResponse(BaseModel):
    """Response after successful registration"""
    message: str = "Registration successful. Please verify your email."
    user_id: int
    email: str
    verification_sent: bool = True
