"""Schemas package for type-safe inter-agent communication."""

from .messages import (
    UserQuery,
    PlannerOutput,
    LegalSource,
    ResearchOutput,
    ReasoningOutput,
    ValidationIssue,
    ValidationOutput,
    SynthesizerOutput,
    RefusalOutput,
    AuditLogEntry,
)

# Authentication schemas
from .lawyers import (
    LawyerBase,
    LawyerCreate,
    LawyerRegister,
    LawyerLogin,
    LawyerResponse,
    LawyerProfileResponse,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    MFASetupResponse,
    MFAEnable,
    MFAVerify,
    SessionResponse,
)

from .admin import (
    AdminBase,
    AdminRegister,
    AdminLogin,
    AdminResponse,
    AdminUpdate,
    AdminPasswordChange,
    AdminMFASetupResponse,
    AdminMFAEnable,
    AdminSessionResponse,
    AdminListResponse,
)

from .auth import (
    Token,
    TokenRefresh,
    TokenRefreshResponse,
    LoginResponse,
    MFARequiredResponse,
    LogoutResponse,
    MessageResponse,
    ErrorResponse,
    PasswordResetEmailSentResponse,
    EmailVerificationSentResponse,
    RegistrationResponse,
)

__all__ = [
    # Message schemas
    "UserQuery",
    "PlannerOutput",
    "LegalSource",
    "ResearchOutput",
    "ReasoningOutput",
    "ValidationIssue",
    "ValidationOutput",
    "SynthesizerOutput",
    "RefusalOutput",
    "AuditLogEntry",
    
    # Lawyer schemas
    "LawyerBase",
    "LawyerCreate",
    "LawyerRegister",
    "LawyerLogin",
    "LawyerResponse",
    "LawyerProfileResponse",
    "PasswordChange",
    "PasswordResetRequest",
    "PasswordReset",
    "EmailVerification",
    "MFASetupResponse",
    "MFAEnable",
    "MFAVerify",
    "SessionResponse",
    
    # Admin schemas
    "AdminBase",
    "AdminRegister",
    "AdminLogin",
    "AdminResponse",
    "AdminUpdate",
    "AdminPasswordChange",
    "AdminMFASetupResponse",
    "AdminMFAEnable",
    "AdminSessionResponse",
    "AdminListResponse",
    
    # Auth schemas
    "Token",
    "TokenRefresh",
    "TokenRefreshResponse",
    "LoginResponse",
    "MFARequiredResponse",
    "LogoutResponse",
    "MessageResponse",
    "ErrorResponse",
    "PasswordResetEmailSentResponse",
    "EmailVerificationSentResponse",
    "RegistrationResponse",
]
