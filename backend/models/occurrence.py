"""
Occurrence Model

Represents individual occurrences/events within an incident case.
Allows tracking of recurring harassment or attacks as separate entities.
"""

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.config import Base


class Occurrence(Base):
    """
    Occurrence model for tracking individual events within an incident.
    
    Example: If a user reports cyberbullying as the main incident,
    each new threatening message or attack can be recorded as a separate occurrence.
    """
    __tablename__ = "occurrences"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    date_occurred = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="occurrences")
    evidence = relationship("Evidence", back_populates="occurrence", cascade="all, delete-orphan")
