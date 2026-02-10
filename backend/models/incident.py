"""
Incident Model

Database model for storing user-reported incidents.
"""

from sqlalchemy import Column, Integer, String, Text, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base
import enum


class IncidentStatusEnum(str, enum.Enum):
    """Status of an incident report."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"


class IncidentTypeEnum(str, enum.Enum):
    """Types of incidents that can be reported."""
    CYBERBULLYING = "CYBERBULLYING"
    HARASSMENT = "HARASSMENT"
    STALKING = "STALKING"
    NON_CONSENSUAL_LEAK = "NON_CONSENSUAL_LEAK"
    IDENTITY_THEFT = "IDENTITY_THEFT"
    ONLINE_FRAUD = "ONLINE_FRAUD"
    OTHER = "OTHER"


class Incident(Base):
    """
    Incident model for storing reported legal incidents.
    
    Links to a User for accountability and includes location
    for jurisdiction determination.
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    
    # User association - who reported this incident
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Incident classification
    incident_type = Column(
        Enum(IncidentTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    
    # Core details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    date_occurred = Column(Date, nullable=True)
    
    # Location/Jurisdiction
    location = Column(String(255), nullable=True)  # e.g., "Colombo", "Kandy District"
    jurisdiction = Column(String(100), nullable=True)  # e.g., "Sri Lanka"
    
    # Additional context
    platforms_involved = Column(String(500), nullable=True)
    perpetrator_info = Column(Text, nullable=True)
    evidence_notes = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(
        Enum(IncidentStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=IncidentStatusEnum.SUBMITTED,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="incidents")
    chat_messages = relationship("IncidentChatMessage", back_populates="incident", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    occurrences = relationship("Occurrence", back_populates="incident", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Incident(id={self.id}, title='{self.title}', status='{self.status}')>"
