"""
Models Package

Exports all database models for the SentiLex AI Advocate system.
"""

from .lawyers import Lawyer, AvailabilityEnum, VerificationStatusEnum
from .admin import Admin, AdminRole
from .token_blacklist import TokenBlacklist
from .login_attempt import LoginAttempt
from .active_session import ActiveSession
from .lawyerverificationaudit import LawyerVerificationAudit

__all__ = [
    # User Models
    "Lawyer",
    "Admin",
    
    # Enums
    "AvailabilityEnum",
    "VerificationStatusEnum",
    "AdminRole",
    
    # Security Models
    "TokenBlacklist",
    "LoginAttempt",
    "ActiveSession",
    
    # Audit Models
    "LawyerVerificationAudit",
]
