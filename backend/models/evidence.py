"""
Evidence Model

Database model for tracking uploaded evidence files for incidents.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base


class Evidence(Base):
    """
    Evidence model for storing metadata about uploaded files.
    
    Files are stored on disk, and this model tracks their location,
    type, and size for retrieval and management.
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    
    # Incident association
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    
    # File metadata
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Stored path on disk
    file_type = Column(String(100), nullable=True)   # MIME type
    file_size = Column(Integer, nullable=True)       # Size in bytes
    
    # Timestamp
    uploaded_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="evidence")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name='{self.file_name}', incident_id={self.incident_id})>"
