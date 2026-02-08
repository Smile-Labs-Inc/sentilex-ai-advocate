"""
Evidence Schemas

Pydantic schemas for evidence API requests and responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EvidenceResponse(BaseModel):
    """Schema for evidence response"""
    id: int
    incident_id: int
    occurrence_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: datetime
    description: Optional[str] = None

    class Config:
        from_attributes = True


class EvidenceWithIncidentResponse(BaseModel):
    """Schema for evidence response with incident details"""
    id: int
    incident_id: int
    occurrence_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: datetime
    description: Optional[str] = None
    
    # Incident details
    incident_title: str
    incident_type: str
    incident_status: str

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    """Schema for paginated evidence list"""
    evidence: list[EvidenceResponse]
    total: int


class EvidenceWithIncidentListResponse(BaseModel):
    """Schema for paginated evidence list with incident details"""
    evidence: list[EvidenceWithIncidentResponse]
    total: int
