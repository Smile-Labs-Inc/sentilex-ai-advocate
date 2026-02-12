"""
Incident Schemas

Pydantic schemas for incident API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class IncidentStatusEnum(str, Enum):
    """Status of an incident report."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"


class IncidentTypeEnum(str, Enum):
    """Types of incidents that can be reported."""
    CYBERBULLYING = "cyberbullying"
    HARASSMENT = "harassment"
    STALKING = "stalking"
    NON_CONSENSUAL_LEAK = "non-consensual-leak"
    IDENTITY_THEFT = "identity-theft"
    ONLINE_FRAUD = "online-fraud"
    OTHER = "other"


class IncidentBase(BaseModel):
    """Base schema with common incident fields."""
    incident_type: IncidentTypeEnum
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    date_occurred: Optional[date] = None
    location: Optional[str] = Field(None, max_length=255)
    jurisdiction: Optional[str] = Field(None, max_length=100)
    platforms_involved: Optional[str] = Field(None, max_length=500)
    perpetrator_info: Optional[str] = None
    evidence_notes: Optional[str] = None


class IncidentCreate(IncidentBase):
    """Schema for creating a new incident."""
    pass


class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""
    incident_type: Optional[IncidentTypeEnum] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    date_occurred: Optional[date] = None
    location: Optional[str] = Field(None, max_length=255)
    jurisdiction: Optional[str] = Field(None, max_length=100)
    platforms_involved: Optional[str] = Field(None, max_length=500)
    perpetrator_info: Optional[str] = None
    evidence_notes: Optional[str] = None
    status: Optional[IncidentStatusEnum] = None


class IncidentResponse(IncidentBase):
    """Schema for incident responses."""
    id: int
    user_id: int
    status: IncidentStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Schema for listing incidents."""
    incidents: list[IncidentResponse]
    total: int


# ============================================================================
# Incident Chat Schemas
# ============================================================================

class IncidentChatRoleEnum(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IncidentChatMessageCreate(BaseModel):
    """Schema for creating an incident chat message."""
    content: str = Field(..., min_length=1)


class IncidentChatMessageResponse(BaseModel):
    """Schema for incident chat message responses."""
    id: int
    incident_id: int
    user_id: Optional[int]
    role: IncidentChatRoleEnum
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentChatExchangeResponse(BaseModel):
    """Schema for chat exchange (user message + AI response)."""
    user_message: IncidentChatMessageResponse
    assistant_message: IncidentChatMessageResponse


# ============================================================================
# Evidence Schemas
# ============================================================================

class EvidenceResponse(BaseModel):
    """Schema for evidence responses."""
    id: int
    incident_id: int
    occurrence_id: Optional[int] = None
    file_name: str
    file_key: Optional[str] = None
    file_hash: Optional[str] = None
    file_type: Optional[str]
    file_size: Optional[int]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    """Schema for listing evidence."""
    evidence: list[EvidenceResponse]
    total: int

