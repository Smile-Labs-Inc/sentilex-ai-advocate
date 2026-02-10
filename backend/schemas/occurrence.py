"""
Occurrence Schemas

Pydantic schemas for occurrence API validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class OccurrenceBase(BaseModel):
    """Base schema with common occurrence fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Brief title of the occurrence")
    description: str = Field(..., min_length=1, description="Detailed description of what happened")
    date_occurred: date = Field(..., description="Date when this occurrence happened")


class OccurrenceCreate(OccurrenceBase):
    """Schema for creating a new occurrence."""
    pass


class OccurrenceUpdate(BaseModel):
    """Schema for updating an occurrence."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    date_occurred: Optional[date] = None


class OccurrenceResponse(OccurrenceBase):
    """Schema for occurrence responses."""
    id: int
    incident_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OccurrenceListResponse(BaseModel):
    """Schema for listing occurrences."""
    occurrences: list[OccurrenceResponse]
    total: int
