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
from .incident_chat import IncidentChatMessage, IncidentChatRoleEnum
from .session_chat import SessionChatMessage, ChatSession
from .evidence import Evidence
from .notification import Notification, RecipientTypeEnum, NotificationTypeEnum

__all__ = [
    # User Models
    "Lawyer",
    "Admin",
    "Incident",
    "IncidentChatMessage",
    "SessionChatMessage",
    "ChatSession",
    "Evidence",
    "Notification",
    
    # Enums
    "AvailabilityEnum",
    "VerificationStatusEnum",
    "AdminRole",
    "IncidentStatusEnum",
    "IncidentTypeEnum",
    "IncidentChatRoleEnum",
    "RecipientTypeEnum",
    "NotificationTypeEnum",
    
    # Security Models
    "TokenBlacklist",
    "LoginAttempt",
    "ActiveSession",
    
    # Audit Models
    "LawyerVerificationAudit",
]
