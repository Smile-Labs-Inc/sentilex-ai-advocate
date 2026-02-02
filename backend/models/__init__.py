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
from .incident import Incident, IncidentStatusEnum, IncidentTypeEnum

__all__ = [
    # User Models
    "Lawyer",
    "Admin",
    "Incident",
    
    # Enums
    "AvailabilityEnum",
    "VerificationStatusEnum",
    "AdminRole",
    "IncidentStatusEnum",
    "IncidentTypeEnum",
    
    # Security Models
    "TokenBlacklist",
    "LoginAttempt",
    "ActiveSession",
    
    # Audit Models
    "LawyerVerificationAudit",
]
